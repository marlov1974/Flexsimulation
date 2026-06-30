# P0004 Functions

## Added or changed functions

- `create_residual_load_diagnostics(result, households)` creates all P0004 diagnostics from a P0003 result.
- `create_portfolio_summary(portfolio)` creates portfolio-level level, volatility and forecast-error metrics.
- `create_site_segment_summary(site)` creates site-segment diagnostics without timestep double-counting.
- `create_household_summary(household)` creates household diagnostics and metadata groupings when available.
- `create_hourly_shape(portfolio)` creates 24-row portfolio hourly shape diagnostics.
- `create_monthly_shape(portfolio)` creates monthly portfolio shape diagnostics.
- `create_forecast_error_summary(site, household, portfolio)` creates site, household and portfolio error diagnostics.
- `create_quality_checks(site, household, portfolio)` creates pass/fail consistency checks.
- `export_diagnostics_to_csv(result, output_dir)` writes one CSV per diagnostics table.

## Public interfaces expected

- Create residual-load diagnostics from a P0003 result.
- Portfolio summary diagnostics.
- Site-segment diagnostics.
- Household diagnostics.
- Hourly and monthly shape diagnostics.
- Forecast-error diagnostics.
- Quality checks.
- CSV export helper.

## Data contracts

- Diagnostics use aggregate site, household and portfolio time-series values.
- Forecast error is actual minus expected.
- Units must be explicit in column names.
- Site diagnostics are enriched from stock metadata when `size_class` is not present in P0003 site output.
- Household diagnostics are enriched from stock metadata for `site_configuration` and `persons_count`.

## Test coverage

- Portfolio summary metrics and load factor.
- Site segment groups and site-count de-duplication.
- Household metadata enrichment.
- Hourly shape, monthly shape and forecast-error tables.
- Full-year default quality checks.
- CSV export to a temporary directory.
