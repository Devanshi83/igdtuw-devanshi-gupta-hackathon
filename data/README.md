# Data sources and assumptions

| Files | Nature | Purpose / source |
|---|---|---|
| synthetic_portfolio.csv | Author-created synthetic | Six long-only USD market values. Fictional issuers, no quantities or instrument risk factors. |
| sample_news.json, sample_social_posts.json | Author-created synthetic | Editable demonstration headlines, including ambiguity and negation cases. Social posts are unverified examples. |
| scenarios.json | Author-selected illustrative assumptions | Asset-type percentage shocks at intensity 10; linearly scaled. No calibration claim. |
| market_data/price_cache.csv | Public historical research sample | Prior Yahoo Finance retrieval via yfinance; data are retained unchanged from the local research artifacts. Original adjusted-price treatment is reported in those artifacts; cache alone cannot independently authenticate vendor provenance. |
| manifest.json | Derived checksums | SHA-256 integrity fingerprints for committed inputs. |

All runtime prototype inputs are included here. Aggregate research outputs live under results/.

Financial PhraseBank is **optional evaluation data**, acquired separately from https://huggingface.co/datasets/takala/financial_phrasebank (Malo et al., 2014), configuration sentences_75agree, CC BY-NC-SA 3.0. Use the research requirements and evaluation script. Preserve its attribution/license. Raw sentence outputs are excluded from Git, including examples in narrative reports. The prototype and offline demo do not need the dataset download.

Yahoo Finance historical data: https://finance.yahoo.com/ . yfinance is a third-party retrieval library: https://github.com/ranaroussi/yfinance . Public availability does not imply unrestricted commercial reuse. Research inputs retain source terms and are not relicensed under the project's MIT software license. The cache is a small personal/educational research sample; no paid or confidential feed is used.

Portfolio CSV columns: asset_id (unique), asset_name, asset_type (Equity/Bond/Loan/Derivative), issuer (non-empty), market_value (finite non-negative number); sector is optional. Unknown asset types fail validation rather than silently receiving zero shock.
