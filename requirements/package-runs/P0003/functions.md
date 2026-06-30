# P0003 Functions

## Added or changed functions

- `SimulationContext.expected_kw(...)`/`actual_kw(...)` support was added to every P0002 base-load object.
- `create_2025_time_index(step_minutes)` creates the timezone-naive 2025 15-minute index.
- `create_simulation_contexts(timestamps, step_minutes)` creates time-aware simulation contexts.
- `stable_seed(base_seed, timestep, object_id)` creates deterministic per-object/per-timestep seeds.
- `simulate_base_load_timeseries(households, config)` returns site, household, portfolio and summary outputs.
- `summarize_base_load_result(portfolio, site_count, household_count)` returns portfolio-level summary metrics.

## Public interfaces expected

- Power-first base-load object methods:
  - `expected_kw(context)`
  - `actual_kw(context, rng)`
- 2025 15-minute time-index helper.
- Base-load time-series simulator.
- Result object with site, household, portfolio and summary outputs.

## Data contracts

- kW is the primary timestep signal.
- kWh and MWh are derived from kW/MW and `step_hours`.
- Normal outputs expose aggregate values only.
- Object-level rows are omitted by default and are only available through explicit debug mode.

## Test coverage

- 2025 time index length and endpoints.
- Time-aware context derived properties.
- Stable seed determinism and object specificity.
- kWh derivation from kW.
- Full-year site, household and portfolio row counts for generated stock.
- Reproducible time series for same stock and simulation seed.
- Portfolio totals independent of load-object iteration order.
- Normal outputs do not include object-level fields.
