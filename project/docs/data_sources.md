# Data Sources and Ingestion Rules

## SPY Daily OHLCV

- **Provider:** Nasdaq public historical endpoint
- **Endpoint:** `https://api.nasdaq.com/api/quote/SPY/historical`
- **Query:** ETF asset class; a ten-year date range; `limit=5000`
- **Fields retained:** `date`, `open`, `high`, `low`, `close`, `volume`
- **Price convention:** unadjusted OHLCV as returned by Nasdaq. This raw source is not an adjusted-return series; later preprocessing must make and document any corporate-action or return-convention decision.
- **Storage:** timestamped CSV in `data/raw/`, with a separate JSON manifest containing query parameters, validation results, SHA-256 checksum, and acquisition time.

## Validation Rules

The pipeline fails if required columns are missing, dates cannot be parsed, numeric columns are invalid, dates repeat or are non-monotonic, prices are nonpositive, volume is negative, or OHLC ranges are inconsistent. A small number of incomplete provider rows may be excluded only when their dates and count are recorded in the manifest; more than 1% incomplete rows fail the run.

## Assumptions and Risks

- Nasdaq's public endpoint is not a contractual data service; availability, access policy, schema, and rate limits can change.
- The snapshot captures data available at its acquisition time; vendors may later revise history.
- The raw unadjusted close must not be silently treated as an adjusted close when building the Stage01 high-volatility target.
- This source supports predictive research and does not establish causal explanations or investment advice.
