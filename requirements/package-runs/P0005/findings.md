# P0005 Findings

## Modelling findings

Heating should be modelled as weather-driven thermal demand converted to electrical load by technology-specific behaviour. P0005 keeps the boundary clear: uncontrolled heating is load, controllable heating is a future asset.

## Technical findings

Heating objects require outdoor temperature in the simulation context. The weather source should be abstracted through a temperature provider, not hard-coded to a local database or external project.

## Bugs or mismatches found

- P0003 originally had no outdoor-temperature channel in `SimulationContext`; P0005 extended it.
- P0003 vectorized normal path originally only recognised P0002 base-load objects; P0005 added explicit heating-object handling.

## Decisions made

Use a synthetic first-pass market proxy for heating-type weights and document it as calibration assumption.

## Tradeoffs

Only one primary uncontrolled heating object per house/cabin in P0005. Hybrid systems, supplements, comfort deficit and domestic hot water are deferred.

## Evidence

- `.venv/bin/python -m pytest` passed with 45 tests.
- `.venv/bin/python -m ruff check .` passed.
- Default 100-household full-year heating simulation increased annual portfolio load from 286.314 MWh to 1,619.263 MWh and passed P0004 quality checks.

## Follow-up candidates

Calibrate heating-type distribution and weather data later. Add controllable heating assets in a future package.
