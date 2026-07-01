# P0003 Findings

## Modelling findings

Power is the primary timestep signal. Energy should be derived from power and timestep duration.

## Technical findings

Deterministic per-object/per-timestep RNG is important so results do not depend on iteration order and can later be parallelised.

## Bugs or mismatches found

No package-specific bugs documented in the original P0003 review.

## Decisions made

Use kW/MW as primary time-series outputs and derive kWh/MWh from `step_hours`.

## Tradeoffs

P0003 stores full-year data in tables/DataFrames. This is acceptable for the current stock size but may need run artifacts or Parquet later.

## Evidence

See `requirements/package-runs/P0003/review.md`.

## Follow-up candidates

Add file-based run persistence before scenario comparison becomes large.
