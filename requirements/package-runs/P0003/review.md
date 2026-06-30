# P0003 Review

## Summary

Implemented the base-load time-series simulator for full-year 2025 using kW as the primary timestep signal.

## Acceptance criteria status

- Object contract: implemented.
- Time index: implemented.
- Simulation: implemented for site, household and portfolio aggregates.
- Reproducibility: implemented with stable per-object/per-timestep deterministic values.
- Object behaviour: preserved from P0002 with power-first methods.
- Boundary: normal outputs expose aggregate base-load values only.

## Tests run

- `.venv/bin/python -m pytest`
  - 27 passed
- `.venv/bin/python -m ruff check .`
  - All checks passed
- Default 100-household full-year smoke:
  - site rows: 4,695,360
  - household rows: 3,504,000
  - portfolio rows: 35,040
  - annual actual base load: 272,702.9 kWh

## Risks and follow-up

- Full-year default stock simulation is vectorized and functional but not yet optimized for 10,000-household scale.
- Object-level debug output exists behind an explicit flag and must remain out of ML/bidding observations.
- Future packages should decide how to persist or stream large annual time-series outputs.
