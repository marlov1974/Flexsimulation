# P0002 Findings

## Modelling findings

Synthetic stock generation works best when household, site and load-object generation are separated. `persons_count` is enough for the first family-heavy stock model; `persons_class` is intentionally avoided.

## Technical findings

Object stock can be reproducible with seeded generation while still creating useful variation by site type, size and random factor.

## Bugs or mismatches found

No package-specific bugs documented in the original P0002 review.

## Decisions made

Represent standby as `StandbyClusterObject` units rather than many individual tiny standby devices.

## Tradeoffs

The initial object set is deliberately simple and latent. Behavioural loads and assets are deferred.

## Evidence

See `requirements/package-runs/P0002/review.md`.

## Follow-up candidates

Calibrate stock weights and object parameter ranges later.
