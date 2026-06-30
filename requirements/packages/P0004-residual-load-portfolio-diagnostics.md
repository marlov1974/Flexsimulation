# P0004 Residual-load portfolio diagnostics

## Purpose

Create the first diagnostics layer on top of the P0003 base-load time-series simulator.

P0004 should make the generated 2025 base-load portfolio understandable. It should not add new load objects, assets, market logic or behavioural simulation. Its job is to analyse the site, household and portfolio outputs from P0003 and produce compact diagnostic tables that show level, volatility, forecast error and segment differences.

## Business intent

The simulator is intended to support an executive business-case and capability discussion. Before adding PV, batteries, EVs, heat pumps or market activation, the model needs a credible and explainable base-load foundation.

P0004 should answer questions such as:

- What does the synthetic portfolio consume over a year?
- How volatile is base load at site, household and portfolio level?
- How much diversification appears when many small sites are aggregated?
- How do apartments, houses and cabins differ?
- How do small, medium and large/premium sites differ?
- What is the scale of forecast error created by latent object-level randomness?
- Are the generated profiles plausible enough to use as a baseline for the next capability packages?

## Scope

Implement diagnostics for P0003 outputs:

```text
1. Portfolio-level diagnostics
2. Site-segment diagnostics
3. Household diagnostics
4. Time-shape diagnostics
5. Forecast-error diagnostics
6. Lightweight export helpers
```

No charts are required in this package. The output should be tables/dataframes first. Charts or UI can come later.

## Inputs

P0004 should consume a P0003 result object, for example:

```python
BaseLoadTimeSeriesResult
```

Expected P0003 result fields:

```text
site
household
portfolio
summary
```

The diagnostics should work if these are pandas DataFrames.

## Output object

Create a result object such as:

```python
ResidualLoadDiagnosticsResult
```

Suggested fields:

```text
portfolio_summary
site_segment_summary
household_summary
hourly_shape
monthly_shape
forecast_error_summary
quality_checks
```

Each field may be a pandas DataFrame or a dictionary where appropriate. Prefer DataFrames for tabular diagnostics.

## Portfolio summary

Create a portfolio-level summary using the P0003 portfolio time series.

Required metrics:

```text
timestep_count
annual_actual_base_load_mwh
annual_expected_base_load_mwh
mean_actual_base_load_mw
mean_expected_base_load_mw
min_actual_base_load_mw
max_actual_base_load_mw
p01_actual_base_load_mw
p05_actual_base_load_mw
p50_actual_base_load_mw
p95_actual_base_load_mw
p99_actual_base_load_mw
std_actual_base_load_mw
mean_forecast_error_mw
std_forecast_error_mw
mean_abs_forecast_error_mw
p95_abs_forecast_error_mw
```

Also include a simple portfolio diversification metric:

```text
portfolio_load_factor = mean_actual_base_load_mw / max_actual_base_load_mw
```

## Site-segment summary

Create segment diagnostics grouped by:

```text
site_type
site_role
size_class
site_type + size_class
```

Required metrics per segment:

```text
site_count
annual_actual_base_load_kwh_total
annual_expected_base_load_kwh_total
annual_actual_base_load_kwh_per_site_mean
annual_actual_base_load_kwh_per_site_p50
mean_actual_base_load_kw_per_site
p05_actual_base_load_kw_per_site
p50_actual_base_load_kw_per_site
p95_actual_base_load_kw_per_site
std_actual_base_load_kw_per_site
mean_abs_forecast_error_kw_per_site
```

Interpretation principle:

- Aggregations should not double-count sites.
- Annual per-site values should be calculated per site first, then summarised across sites.
- Instantaneous per-site distributions should be calculated from site timestep rows.

## Household summary

Create household-level diagnostics.

Required metrics:

```text
household_count
annual_actual_base_load_kwh_per_household_mean
annual_actual_base_load_kwh_per_household_p05
annual_actual_base_load_kwh_per_household_p50
annual_actual_base_load_kwh_per_household_p95
mean_actual_base_load_kw_per_household
p95_actual_base_load_kw_per_household
mean_abs_forecast_error_kw_per_household
```

Also group by:

```text
site_configuration
persons_count
```

If `site_configuration` or `persons_count` are not present in P0003 household time series, enrich from the generated stock/household objects or require the caller to pass household metadata.

## Time-shape diagnostics

Create compact time-shape tables for the portfolio.

Required outputs:

### Hourly shape

Grouped by hour of day:

```text
hour
mean_actual_base_load_mw
p05_actual_base_load_mw
p50_actual_base_load_mw
p95_actual_base_load_mw
mean_forecast_error_mw
mean_abs_forecast_error_mw
```

### Monthly shape

Grouped by month:

```text
month
annualised_or_period_actual_base_load_mwh
mean_actual_base_load_mw
p05_actual_base_load_mw
p50_actual_base_load_mw
p95_actual_base_load_mw
mean_forecast_error_mw
mean_abs_forecast_error_mw
```

Use the actual period MWh for each month, not annualised MWh, unless explicitly named otherwise.

## Forecast-error diagnostics

Forecast error is always:

```text
actual - expected
```

Create diagnostics for portfolio, site and household levels.

Required metrics:

```text
mean_forecast_error
mean_abs_forecast_error
std_forecast_error
p05_forecast_error
p50_forecast_error
p95_forecast_error
p95_abs_forecast_error
```

Use unit suffixes in column names:

```text
_kw
_mw
_kwh
_mwh
```

## Quality checks

Add a quality-check output that tests basic consistency of the generated diagnostics.

Required checks:

```text
portfolio_timestep_count_is_35040
portfolio_has_no_negative_actual_load
portfolio_has_no_negative_expected_load
forecast_error_equals_actual_minus_expected
portfolio_mwh_equals_mw_times_0_25
site_kwh_equals_kw_times_0_25
household_kwh_equals_kw_times_0_25
site_to_portfolio_energy_reconciles
household_to_portfolio_energy_reconciles
```

The quality-check result should include:

```text
check_name
passed
detail
```

## Export helpers

Add a lightweight export helper that can write diagnostics to CSV files.

Suggested function:

```python
export_diagnostics_to_csv(result, output_dir) -> list[Path]
```

It should write one CSV per diagnostics table and return the created paths.

This should not be required for normal operation, but should be tested with a temporary directory.

## Public-safe requirement

Use only synthetic and neutral examples. Do not add company names, real customer data, real prices, real production data or internal commercial terms.

## Acceptance criteria

### Diagnostics result

- A `ResidualLoadDiagnosticsResult` or equivalent result object exists.
- It contains portfolio summary, site-segment summary, household summary, hourly shape, monthly shape, forecast-error summary and quality checks.
- Diagnostics can be created from a default P0003 simulation result.

### Portfolio diagnostics

- Portfolio diagnostics include annual actual and expected MWh.
- Portfolio diagnostics include p01, p05, p50, p95 and p99 actual MW.
- Portfolio diagnostics include forecast-error metrics.
- Portfolio load factor is calculated as mean actual MW divided by max actual MW.

### Site-segment diagnostics

- Site diagnostics group by `site_type`.
- Site diagnostics group by `site_role`.
- Site diagnostics group by `size_class`.
- Site diagnostics group by combined `site_type + size_class`.
- Annual per-site values are calculated per site before segment summary.
- Segment site counts are correct and do not count each timestep as a site.

### Household diagnostics

- Household diagnostics include annual kWh per household distribution.
- Household diagnostics include mean, p05, p50 and p95 annual actual kWh per household.
- Household diagnostics can group by `site_configuration` and `persons_count` when metadata is available.

### Time-shape diagnostics

- Hourly shape has exactly 24 rows.
- Monthly shape has exactly 12 rows.
- Hourly and monthly diagnostics include mean, p05, p50 and p95 actual MW.

### Forecast-error diagnostics

- Forecast error is calculated as actual minus expected.
- Mean absolute forecast error is included.
- p95 absolute forecast error is included.
- Units are explicit in column names.

### Quality checks

- Quality-check output exists.
- Quality checks include boolean pass/fail values.
- Energy reconciliation checks compare site and household totals to portfolio totals within a numeric tolerance.
- Normal diagnostics do not expose object-level states.

### Export

- CSV export helper writes diagnostics tables to a provided output directory.
- Export helper returns created paths.
- Export helper works in a temporary test directory.

## Out of scope

- Plotting or chart rendering.
- Interactive web page.
- New load objects.
- PV, batteries, EVs or heat pumps.
- Market bidding, activation, rebound or settlement.
- Calibration to real measurement data.
- Persisting large simulation outputs as Parquet.

## Suggested implementation files

```text
src/flexsimulation/residual_load_diagnostics.py
tests/test_residual_load_diagnostics.py
```

Existing P0003 result types may be extended if needed, but avoid changing P0003 behaviour unless required for metadata enrichment.

## Package-run updates required

After implementation, update:

```text
requirements/package-runs/P0004/design.md
requirements/package-runs/P0004/functions.md
requirements/package-runs/P0004/review.md
REPOSITORY_FILES.md
```

Run:

```text
python -m pytest
ruff check .
```
