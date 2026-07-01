# P0005 Review

## Summary

Implemented uncontrolled weather-driven heating load objects and P0003 time-series integration.

## Acceptance criteria status

- Demand and weather: implemented.
- Heating objects: implemented.
- Technology behaviour: implemented.
- Factory and eligibility: implemented.
- Time-series integration: implemented.
- P0004 diagnostics compatibility: implemented.
- Boundary: heating objects remain non-controllable latent load objects.

## Tests run

- `.venv/bin/python -m pytest`
  - 45 passed
- `.venv/bin/python -m ruff check .`
  - All checks passed
- Default 100-household full-year heating smoke:
  - base actual load: 286.314 MWh
  - heating-enriched actual load: 1,619.263 MWh
  - heating uplift: 1,332.949 MWh
  - portfolio rows: 35,040
  - site rows: 4,870,560
  - P0004 quality checks passed

## Risks and follow-up

- Synthetic temperature and heating-type weights are first-pass public-safe assumptions, not calibrated statistics.
- Heating objects are uncontrolled load/risk only; controllable heating assets remain future package scope.
- Full-year heating simulation works for default stock, but larger scale may need more vectorization.
