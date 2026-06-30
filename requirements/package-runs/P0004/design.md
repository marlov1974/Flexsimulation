# P0004 Design

## Goal

Implement residual-load portfolio diagnostics on top of the P0003 base-load time-series result.

## Consistency review

- Active package: P0004-residual-load-portfolio-diagnostics
- Files expected to change:
  - `src/flexsimulation/residual_load_diagnostics.py`
  - `tests/test_residual_load_diagnostics.py`
- Observation-boundary impact:
  - normal diagnostics must expose aggregate site, household and portfolio values only
  - object-level states remain latent/debug and are not diagnostics outputs
- Business-case impact:
  - makes the base-load portfolio explainable before adding PV, battery, EV, heat pump and market-capability packages
- Tests required:
  - portfolio summary metrics exist
  - segment groupings exist and do not double-count sites
  - hourly shape has 24 rows
  - monthly shape has 12 rows
  - quality checks pass on a default P0003 result
  - CSV export works in temporary directory

## Design

See `requirements/packages/P0004-residual-load-portfolio-diagnostics.md`.

## Open questions

- If P0003 household output lacks `site_configuration` and `persons_count`, P0004 should enrich from stock metadata rather than weakening diagnostics.
- Charting is intentionally out of scope for this package.
