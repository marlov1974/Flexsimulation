# P0005 Design

## Goal

Implement uncontrolled, weather-driven heating load objects for house and cabin sites.

## Consistency review

- Active package: P0005-uncontrolled-heating-load-objects
- Files expected to change:
  - `src/flexsimulation/temperature.py`
  - `src/flexsimulation/heating_demand.py`
  - `src/flexsimulation/heating_load_objects.py`
  - `src/flexsimulation/heating_load_factory.py`
  - P0003 simulation context / timeseries integration as needed
  - tests for heating demand, temperature, load objects, factory and integration
- Observation-boundary impact:
  - heating objects remain latent load objects
  - normal time-series/diagnostic outputs expose aggregate base-load values only
- Business-case impact:
  - adds the first cold-weather residual-load driver and prepares the contrast between uncontrolled heating load and future controllable heating assets
- Tests required:
  - thermal need increases when outdoor temperature decreases
  - all heating objects return non-negative kW
  - air-source COP/capacity decrease when colder
  - heat pumps use backup when underdimensioned
  - house/cabin get one primary heating object; apartment gets none
  - full-year 2025 simulation works with synthetic temperature and P0004 diagnostics

## Design

See `requirements/packages/P0005-uncontrolled-heating-load-objects.md`.

## Open questions

- Default heating market weights are synthetic proxy assumptions and should be calibrated later.
- External/local weather data integration is intentionally out of scope for P0005.
- Hybrid heating systems and supplemental direct-electric elements are deferred.
