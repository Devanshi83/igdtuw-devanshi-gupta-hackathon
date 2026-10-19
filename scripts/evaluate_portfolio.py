"""Evaluate portfolio stress calculations against hand-calculated results."""

import pandas as pd

from src.risk.stress import stress_portfolio


PORTFOLIO = pd.DataFrame(
    [
        {
            "asset_name": "Technology Equity",
            "asset_type": "Equity",
            "issuer": "Example Technology Ltd",
            "market_value": 250_000.0,
        },
        {
            "asset_name": "Banking Equity",
            "asset_type": "Equity",
            "issuer": "Example Bank Ltd",
            "market_value": 200_000.0,
        },
        {
            "asset_name": "Corporate Bond",
            "asset_type": "Bond",
            "issuer": "Example Technology Ltd",
            "market_value": 150_000.0,
        },
        {
            "asset_name": "Bank Loan",
            "asset_type": "Loan",
            "issuer": "Example Bank Ltd",
            "market_value": 250_000.0,
        },
        {
            "asset_name": "Government Bond",
            "asset_type": "Bond",
            "issuer": "Example Government",
            "market_value": 200_000.0,
        },
        {
            "asset_name": "Interest Rate Swap",
            "asset_type": "Derivative",
            "issuer": "Example Bank Ltd",
            "market_value": 100_000.0,
        },
    ]
)

TOTAL_VALUE = 1_150_000.0
TOLERANCE = 0.01


def check_close(label, actual, expected):
    passed = abs(float(actual) - expected) <= TOLERANCE
    print(
        f"  {'PASS' if passed else 'FAIL'} {label}: "
        f"actual={float(actual):,.2f}, expected={expected:,.2f}"
    )
    return passed


def check_case(name, event, target, expected_pnl, expected_affected,
               expected_position_pnl, impact=9):
    print(f"\n{name}")
    result = stress_portfolio(
        PORTFOLIO,
        event,
        impact,
        target_company=target,
    )

    checks = [
        check_close(
            "Starting portfolio value",
            result["market_value"].sum(),
            TOTAL_VALUE,
        ),
        check_close(
            "Total portfolio P&L",
            result["pnl"].sum(),
            expected_pnl,
        ),
        check_close(
            "Ending portfolio value",
            result["value_after"].sum(),
            TOTAL_VALUE + expected_pnl,
        ),
    ]

    affected_count = int(result["affected"].sum())
    affected_ok = affected_count == expected_affected
    print(
        f"  {'PASS' if affected_ok else 'FAIL'} Affected positions: "
        f"{affected_count}, expected={expected_affected}"
    )
    checks.append(affected_ok)

    for asset_name, expected in expected_position_pnl.items():
        actual_rows = result.loc[result["asset_name"] == asset_name, "pnl"]
        if len(actual_rows) != 1:
            print(f"  FAIL Position missing or duplicated: {asset_name}")
            checks.append(False)
            continue
        checks.append(
            check_close(f"{asset_name} P&L", actual_rows.iloc[0], expected)
        )

    return checks


def main():
    all_checks = []

    # Macroeconomic at 9/10: all six positions are in scope.
    all_checks += check_case(
        name="1. Systemic Macroeconomic scenario at intensity 9/10",
        event="Macroeconomic",
        target=None,
        expected_pnl=-63_000.0,
        expected_affected=6,
        expected_position_pnl={
            "Technology Equity": -18_000.0,
            "Banking Equity": -14_400.0,
            "Corporate Bond": -5_400.0,
            "Bank Loan": -13_500.0,
            "Government Bond": -7_200.0,
            "Interest Rate Swap": -4_500.0,
        },
    )

    # Credit Event: only Example Technology Ltd positions are affected.
    all_checks += check_case(
        name="2. Issuer-specific Credit Event at intensity 9/10",
        event="Credit Event",
        target="Example Technology Ltd",
        expected_pnl=-40_500.0,
        expected_affected=2,
        expected_position_pnl={
            "Technology Equity": -27_000.0,
            "Corporate Bond": -13_500.0,
            "Banking Equity": 0.0,
            "Bank Loan": 0.0,
            "Government Bond": 0.0,
            "Interest Rate Swap": 0.0,
        },
    )

    # Unknown issuer: no positions should be affected.
    all_checks += check_case(
        name="3. Credit Event for a nonexistent issuer",
        event="Credit Event",
        target="Nonexistent Company Ltd",
        expected_pnl=0.0,
        expected_affected=0,
        expected_position_pnl={
            "Technology Equity": 0.0,
            "Banking Equity": 0.0,
            "Corporate Bond": 0.0,
            "Bank Loan": 0.0,
            "Government Bond": 0.0,
            "Interest Rate Swap": 0.0,
        },
    )

    # Merger/Acquisition has a positive Equity shock at the target issuer.
    all_checks += check_case(
        name="4. Merger/Acquisition for Example Technology Ltd",
        event="Merger/Acquisition",
        target="Example Technology Ltd",
        expected_pnl=4_500.0,
        expected_affected=2,
        expected_position_pnl={
            "Technology Equity": 4_500.0,
            "Corporate Bond": 0.0,
            "Banking Equity": 0.0,
            "Bank Loan": 0.0,
            "Government Bond": 0.0,
            "Interest Rate Swap": 0.0,
        },
    )

    passed = sum(bool(check) for check in all_checks)
    total = len(all_checks)

    print("\n" + "=" * 48)
    print(f"CHECKS PASSED: {passed}/{total}")
    print("All numerical checks passed." if passed == total
          else "Some checks failed; inspect the results above.")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
