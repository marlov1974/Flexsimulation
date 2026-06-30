# P0003 Design

## Goal

Implement the base-load time-series simulator for full-year 2025 using kW as the primary timestep signal.

## Consistency review

- Active package: P0003-base-load-timeseries-simulator
- Files expected to change:
  - `src/flexsimulation/base_load_objects.py`
  - `src/flexsimulation/simulation_time.py`
  - `src/flexsimulation/base_load_timeseries.py`
  - tests for time index and base-load time series
- Observation-boundary impact:
  - site/household/portfolio outputs must expose aggregate base-load values only
  - object-level details remain latent/debug
- Business-case impact:
  - creates annual residual base-load profiles needed for later solar, battery and bid-risk analysis
- Tests required:
  - 2025 has 35040 15-minute timesteps
  - kWh is derived from kW × step_hours
  - time series row counts are correct
  - same seed produces same series
  - object iteration order does not change portfolio totals

## Design

See `requirements/packages/P0003-base-load-timeseries-simulator.md`.

## Open questions

- Whether normal result storage should use pandas DataFrames or plain rows can be decided during implementation.
- Object-level debug mode can be skipped if it complicates first implementation.
