# P0004 Findings

## Modelling findings

Diagnostics are needed before adding more asset classes so base-load plausibility and volatility can be inspected by portfolio, segment and time shape.

## Technical findings

Segment summaries must count unique sites or households rather than timestep rows. Metadata enrichment is useful when simulation outputs do not carry all segmentation fields.

## Bugs or mismatches found

A fallback grouping without `size_class` was noted as a possible cleanup candidate, but normal usage enriches `size_class` from stock metadata.

## Decisions made

Keep P0004 table-based. Plotting and UI are deferred.

## Tradeoffs

Diagnostics consume full P0003 outputs in memory. This is acceptable for current scale but should be revisited if population size grows materially.

## Evidence

See `requirements/package-runs/P0004/review.md`.

## Follow-up candidates

Add charts/UI later. Add run persistence before many scenario runs are compared.
