# P0005 Functions

## Added or changed functions

- `SyntheticTemperatureProvider.outdoor_temp_c(timestamp)` provides public-safe synthetic 2025 outdoor temperature.
- `HeatingDemandModel.thermal_need_kw(outdoor_temp_c)` converts outdoor temperature to thermal need.
- `DirectElectricHeatingObject` implements uncontrolled direct-electric heating load.
- `GroundSourceHeatPumpLoadObject` implements uncontrolled ground-source heat-pump load with load-dependent COP.
- `AirAirHeatPumpLoadObject` implements uncontrolled air-air heat-pump load with temperature-dependent COP and capacity.
- `AirWaterHeatPumpLoadObject` implements uncontrolled air-water heat-pump load with temperature-dependent COP and capacity.
- `ExhaustAirHeatPumpLoadObject` implements uncontrolled exhaust-air heat-pump load and electric backup.
- `PelletStoveLoadObject` implements pellet-stove auxiliary electric load.
- `generate_uncontrolled_heating_objects_for_site(site, rng, config)` creates eligible site heating objects.
- `generate_uncontrolled_heating_objects_for_sites(sites, seed, config)` creates heating objects keyed by site.
- `add_uncontrolled_heating_objects(households, seed, config)` appends heating load objects to generated stock.
- `BaseLoadTimeSeriesConfig.temperature_provider` passes outdoor temperature into P0003 simulation contexts.

## Public interfaces expected

- Temperature provider abstraction.
- Synthetic temperature provider.
- Heating demand model.
- Uncontrolled heating load objects:
  - direct electric
  - ground-source heat pump
  - air-air heat pump
  - air-water heat pump
  - exhaust-air heat pump
  - pellet stove
- Heating load factory for house and cabin sites.
- Optional P0003 simulator extension to pass outdoor temperature into context.

## Data contracts

- kW remains the primary timestep signal.
- Heating objects are non-controllable load objects.
- `heating_role = primary` for P0005-generated objects.
- No hard-coded external weather/database dependency.
- Heating objects require `outdoor_temp_c` and fail clearly when it is missing.
- House and cabin sites receive one primary uncontrolled heating object; apartment sites receive none.

## Test coverage

- Synthetic temperature seasonality.
- Heating demand non-negativity and cold-weather increase.
- Power-first contract and non-negative kW for all heating object types.
- Air-source COP and capacity degradation in cold weather.
- Heat-pump backup behaviour.
- Pellet-stove auxiliary electric load.
- Heating factory eligibility, weights and reproducibility.
- P0003 full-year time-series integration with synthetic temperature.
- P0004 diagnostics compatibility with heating-enriched base load.
