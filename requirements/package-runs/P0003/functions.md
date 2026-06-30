# P0003 Functions

## Added or changed functions

To be completed during implementation.

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

## Test coverage

To be completed during implementation.
