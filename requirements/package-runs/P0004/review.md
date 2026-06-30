# P0004 Review

## Summary

Implemented residual-load portfolio diagnostics on top of the P0003 base-load time-series result.

## Acceptance criteria status

- Diagnostics result: implemented.
- Portfolio diagnostics: implemented.
- Site-segment diagnostics: implemented with site metadata enrichment.
- Household diagnostics: implemented with household metadata enrichment.
- Time-shape diagnostics: implemented.
- Forecast-error diagnostics: implemented.
- Quality checks: implemented.
- CSV export: implemented.

## Tests run

- `.venv/bin/python -m pytest`
  - 33 passed
- `.venv/bin/python -m ruff check .`
  - All checks passed

## Risks and follow-up

- Full-year diagnostics are table-based and pass consistency checks, but no charting is included by design.
- P0003 result tables can be large; future packages should decide whether diagnostics consume streamed or persisted outputs.
- Object-level states remain outside normal diagnostics outputs.
