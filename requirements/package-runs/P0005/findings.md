# P0005 Findings

## Modelling findings

Heating should be modelled as weather-driven thermal demand converted to electrical load by technology-specific behaviour. P0005 keeps the boundary clear: uncontrolled heating is load, controllable heating is a future asset.

## Technical findings

Heating objects require outdoor temperature in the simulation context. The weather source should be abstracted through a temperature provider, not hard-coded to a local database or external project.

## Bugs or mismatches found

None yet; package is requirements-only at this point.

## Decisions made

Use a synthetic first-pass market proxy for heating-type weights and document it as calibration assumption.

## Tradeoffs

Only one primary uncontrolled heating object per house/cabin in P0005. Hybrid systems, supplements, comfort deficit and domestic hot water are deferred.

## Evidence

See `requirements/packages/P0005-uncontrolled-heating-load-objects.md`.

## Follow-up candidates

Calibrate heating-type distribution and weather data later. Add controllable heating assets in a future package.
