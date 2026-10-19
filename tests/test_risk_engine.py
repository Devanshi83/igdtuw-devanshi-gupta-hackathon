import pandas as pd
import pytest

from src.nlp.analyzer import analyze_text
from src.risk.stress import stress_portfolio


def test_negative_credit_event_is_classified():
    result = analyze_text(
        "The bank reported a major debt default and liquidity concerns."
    )
    assert result["event_classification"] == "Credit Event"
    assert result["sentiment_score"] < 0
    assert result["impact_score"] == 9


def test_positive_text_has_positive_sentiment():
    result = analyze_text(
        "The company reported strong profit growth and record revenue."
    )
    assert result["sentiment_score"] == 1.0


def test_neutral_text_has_zero_sentiment():
    result = analyze_text("The company held its annual meeting.")
    assert result["sentiment_score"] == 0.0
    assert result["event_classification"] == "Other"


def test_empty_text_is_handled():
    result = analyze_text("")
    assert result["sentiment_score"] == 0.0
    assert result["event_classification"] == "Other"


def test_non_string_text_is_rejected():
    with pytest.raises(TypeError):
        analyze_text(None)


def test_impact_must_be_between_one_and_ten():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "market_value": [1000.0],
    })
    with pytest.raises(ValueError):
        stress_portfolio(portfolio, "Credit Event", 11)


def test_credit_stress_calculates_expected_values():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity", "Bond", "Loan", "Derivative"],
        "issuer": ["Test Issuer"] * 4,
        "market_value": [1000.0, 1000.0, 1000.0, 1000.0],
    })

    result = stress_portfolio(
        portfolio, "Credit Event", 10, target_company="Test Issuer"
    )

    assert result["value_after"].tolist() == [
        880.0, 900.0, 850.0, 920.0
    ]
    assert result["pnl"].sum() == pytest.approx(-450.0)

def test_original_portfolio_is_not_mutated():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "issuer": ["Test Issuer"],
        "market_value": [1000.0],
    })
    original = portfolio.copy(deep=True)

    stress_portfolio(
        portfolio, "Credit Event", 10, target_company="Test Issuer"
    )

    pd.testing.assert_frame_equal(portfolio, original)

def test_unknown_event_is_rejected():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "market_value": [1000.0],
    })
    with pytest.raises(ValueError):
        stress_portfolio(portfolio, "Unknown Event", 5)


def test_issuer_event_only_affects_target_company():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity", "Loan", "Bond"],
        "issuer": [
            "Example Bank Ltd",
            "Example Bank Ltd",
            "Example Technology Ltd",
        ],
        "market_value": [1000.0, 2000.0, 1500.0],
    })

    result = stress_portfolio(
        portfolio,
        "Credit Event",
        10,
        target_company="Example Bank Ltd",
    )

    assert result["affected"].tolist() == [True, True, False]
    assert result.loc[2, "value_after"] == 1500.0
    assert result.loc[0, "value_after"] == 880.0
    assert result.loc[1, "value_after"] == 1700.0


def test_issuer_matching_is_case_insensitive():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "issuer": ["Example Bank Ltd"],
        "market_value": [1000.0],
    })

    result = stress_portfolio(
        portfolio,
        "Credit Event",
        10,
        target_company="EXAMPLE BANK LTD",
    )

    assert result.loc[0, "affected"]
    assert result.loc[0, "value_after"] == 880.0


def test_issuer_event_requires_target_company():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "issuer": ["Example Bank Ltd"],
        "market_value": [1000.0],
    })

    with pytest.raises(ValueError, match="target company"):
        stress_portfolio(portfolio, "Credit Event", 10)


def test_portfolio_exposure_and_pnl_percentages():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity", "Bond"],
        "issuer": ["Example Bank Ltd", "Example Bank Ltd"],
        "market_value": [1000.0, 3000.0],
    })

    result = stress_portfolio(
        portfolio,
        "Credit Event",
        10,
        target_company="Example Bank Ltd",
    )

    assert "portfolio_weight_pct" in result.columns
    assert "pnl_pct_of_portfolio" in result.columns
    assert result["portfolio_weight_pct"].tolist() == pytest.approx(
        [25.0, 75.0]
    )
    assert result["pnl_pct_of_portfolio"].tolist() == pytest.approx(
        [-3.0, -7.5]
    )


def test_unmatched_issuer_has_no_affected_positions():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "issuer": ["Example Technology Ltd"],
        "market_value": [1000.0],
    })

    result = stress_portfolio(
        portfolio,
        "Credit Event",
        10,
        target_company="Example Bank Ltd",
    )

    assert not result["affected"].any()
    assert (result["pnl"] == 0.0).all()


def test_infinite_market_value_is_rejected():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "issuer": ["Example Bank Ltd"],
        "market_value": [float("inf")],
    })

    with pytest.raises(ValueError):
        stress_portfolio(
            portfolio,
            "Credit Event",
            10,
            target_company="Example Bank Ltd",
        )


def test_zero_value_portfolio_has_finite_results():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "issuer": ["Example Bank Ltd"],
        "market_value": [0.0],
    })

    result = stress_portfolio(
        portfolio,
        "Credit Event",
        10,
        target_company="Example Bank Ltd",
    )

    assert result["value_after"].iloc[0] == 0.0
    assert result["pnl"].iloc[0] == 0.0


def test_unsupported_scenario_scope_is_rejected(monkeypatch):
    import src.risk.stress as stress_module

    monkeypatch.setattr(
        stress_module,
        "load_scenarios",
        lambda: {
            "Credit Event": {
                "scope": "unknown",
                "shocks": {"Equity": -0.12},
            }
        },
    )
    portfolio = pd.DataFrame(
        {"asset_type": ["Equity"], "market_value": [1000.0]}
    )

    with pytest.raises(ValueError, match="Unsupported scenario scope"):
        stress_portfolio(portfolio, "Credit Event", 10)


def test_missing_shock_configuration_is_rejected(monkeypatch):
    import src.risk.stress as stress_module

    monkeypatch.setattr(
        stress_module,
        "load_scenarios",
        lambda: {"Credit Event": {"scope": "systemic"}},
    )
    portfolio = pd.DataFrame(
        {"asset_type": ["Equity"], "market_value": [1000.0]}
    )

    with pytest.raises((ValueError, KeyError, TypeError)):
        stress_portfolio(portfolio, "Credit Event", 10)


def test_non_numeric_shock_is_rejected(monkeypatch):
    import src.risk.stress as stress_module

    monkeypatch.setattr(
        stress_module,
        "load_scenarios",
        lambda: {
            "Credit Event": {
                "scope": "systemic",
                "shocks": {"Equity": "severe"},
            }
        },
    )
    portfolio = pd.DataFrame(
        {"asset_type": ["Equity"], "market_value": [1000.0]}
    )

    with pytest.raises((ValueError, TypeError)):
        stress_portfolio(portfolio, "Credit Event", 10)


def test_valid_scenario_configuration_is_accepted():
    from src.risk.stress import validate_scenario

    scenario = {
        "scope": "issuer",
        "shocks": {"Equity": -0.12, "Bond": 0.02},
    }
    assert validate_scenario(scenario) == scenario


def test_invalid_scenario_scope_is_rejected():
    from src.risk.stress import validate_scenario

    with pytest.raises(ValueError, match="Unsupported scenario scope"):
        validate_scenario({"scope": "unknown", "shocks": {"Equity": -0.1}})


def test_empty_scenario_shocks_are_rejected():
    from src.risk.stress import validate_scenario

    with pytest.raises(ValueError, match="non-empty object"):
        validate_scenario({"scope": "systemic", "shocks": {}})


def test_non_numeric_scenario_shock_is_rejected():
    from src.risk.stress import validate_scenario

    with pytest.raises(ValueError, match="finite number"):
        validate_scenario({"scope": "systemic", "shocks": {"Equity": "severe"}})


@pytest.mark.parametrize("shock", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_scenario_shock_is_rejected(shock):
    from src.risk.stress import validate_scenario

    with pytest.raises(ValueError, match="finite number"):
        validate_scenario({"scope": "systemic", "shocks": {"Equity": shock}})


def test_scenario_shock_below_negative_100_percent_is_rejected():
    from src.risk.stress import validate_scenario

    with pytest.raises(ValueError, match="cannot be less than -1"):
        validate_scenario({"scope": "systemic", "shocks": {"Equity": -1.01}})


def test_positive_scenario_shock_is_allowed():
    from src.risk.stress import validate_scenario

    scenario = {"scope": "issuer", "shocks": {"Equity": 0.02}}
    assert validate_scenario(scenario) == scenario


def test_software_word_does_not_trigger_geopolitical_event():
    result = analyze_text("The software update improved system reliability.")
    assert result["event_classification"] == "Other"


def test_product_event_is_not_overridden_by_software_substring():
    result = analyze_text("The software rollout experienced an outage.")
    assert result["event_classification"] == "Product/Cyber Event"


def test_multiword_event_keyword_matches_with_punctuation():
    result = analyze_text("An interest rate announcement was released.")
    assert result["event_classification"] == "Macroeconomic"


def test_plural_sanctions_are_classified_as_geopolitical():
    from src.nlp.analyzer import analyze_text

    result = analyze_text("New sanctions were announced against the region.")

    assert result["event_classification"] == "Geopolitical"
