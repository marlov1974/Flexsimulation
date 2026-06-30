# P0002 Design

## Goal

Implement the synthetic stock and initial base-load object generator.

## Consistency review

- Active package: P0002-synthetic-stock-and-base-load-object-generator
- Files expected to change:
  - `src/flexsimulation/population.py`
  - `src/flexsimulation/base_load_objects.py`
  - `src/flexsimulation/stock_generator.py`
  - `src/flexsimulation/base_load_factory.py`
  - tests for population and base-load objects
- Observation-boundary impact:
  - object-level details remain latent/debug and must not become ML observations
- Business-case impact:
  - creates the first synthetic stock needed to simulate residual base load and later portfolio risk
- Tests required:
  - reproducible population generation
  - valid site configurations
  - valid object counts
  - non-negative object kWh
  - no `persons_class`

## Design

See `requirements/packages/P0002-synthetic-stock-and-base-load-object-generator.md`.

## Open questions

- Default site-configuration weights should be calibrated later.
- Exact object parameter ranges should be treated as synthetic first-pass assumptions.
