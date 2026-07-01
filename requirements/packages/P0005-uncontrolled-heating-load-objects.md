# P0005 Uncontrolled heating load objects

## Purpose

Add the first complex weather-driven non-controllable load objects.

P0005 should create uncontrolled heating load objects for sites that do not yet have controllable heating assets. These objects should convert outdoor temperature into thermal demand and then into electrical load using heating-system-specific logic.

The package must keep a clear modelling boundary:

```text
uncontrolled heating = load object
controllable heating = future asset object
```

P0005 only implements uncontrolled load objects.

## Business intent

Heating is one of the largest drivers of residual load and forecast risk in a Nordic customer portfolio. Before adding controllable heat pumps, batteries, EVs or flexibility markets, the simulator needs a realistic non-controllable heating baseline.

This package should make the portfolio respond to cold weather:

```text
colder weather
→ higher thermal need
→ higher electric load
→ larger residual-load volatility
→ lower risk-adjusted flexibility later
```

It also creates the future contrast between:

```text
uncontrolled heating = load/risk
controllable heating = flexibility asset/system capability
```

## Scope

Implement:

```text
1. Heating demand model
2. Temperature provider abstraction
3. Uncontrolled heating load object types
4. Heating object factory for eligible sites
5. P0003 time-series integration
6. P0004 diagnostics compatibility
```

No controllable heating, scheduling, activation, rebound or market logic is included.

## Heating object types

Implement these initial uncontrolled heating load object types:

```text
DirectElectricHeatingObject
GroundSourceHeatPumpLoadObject
AirAirHeatPumpLoadObject
AirWaterHeatPumpLoadObject
ExhaustAirHeatPumpLoadObject
PelletStoveLoadObject
```

All objects are non-controllable load objects.

All objects must implement the P0003 power-first contract:

```python
expected_kw(context) -> float
actual_kw(context, rng) -> float
expected_kwh(context) -> float
actual_kwh(context, rng) -> float
```

Energy methods must be derived from kW:

```text
kWh = kW * context.step_hours
```

## Heating demand model

Create a reusable heating demand model.

Suggested class:

```python
HeatingDemandModel
```

Required fields:

```text
balance_temperature_c
design_temperature_c
design_heat_loss_kw
internal_gain_kw
```

Required method:

```python
thermal_need_kw(outdoor_temp_c: float) -> float
```

First implementation formula:

```text
heat_loss_slope_kw_per_c = design_heat_loss_kw / (balance_temperature_c - design_temperature_c)
thermal_need_kw = max(0, heat_loss_slope_kw_per_c * (balance_temperature_c - outdoor_temp_c) - internal_gain_kw)
```

The method must return non-negative thermal kW.

## Temperature and SimulationContext

P0005 needs outdoor temperature for each timestep.

Extend the simulation context so heating objects can access:

```text
outdoor_temp_c
```

Suggested field:

```python
SimulationContext.outdoor_temp_c: float | None = None
```

If a heating object is ticked without outdoor temperature, it should raise a clear error rather than silently returning zero.

## Temperature provider abstraction

Do not hard-code a dependency to any local database or external project.

Create a generic abstraction such as:

```python
TemperatureProvider
```

Required method:

```python
outdoor_temp_c(timestamp) -> float
```

Implement at least:

```text
SyntheticTemperatureProvider
```

Optional, if simple:

```text
CsvTemperatureProvider
```

The synthetic provider should produce plausible Nordic annual seasonality for 2025. It does not need to be calibrated to real weather.

A future package may add an adapter for external weather data or another local simulator project. P0005 must remain public-safe and self-contained.

## Heating load calculation principles

### DirectElectricHeatingObject

Direct electric heating converts thermal need directly to electric load.

Required logic:

```text
electrical_kw = min(max_electric_kw, thermal_need_kw)
```

COP is implicitly 1.0.

Fields should include:

```text
max_electric_kw
demand_model
noise_std_pct
```

### GroundSourceHeatPumpLoadObject

Ground-source heat pump converts thermal need using a relatively stable COP, but COP should decrease mildly under high load.

Required logic:

```text
hp_thermal_kw = min(thermal_need_kw, max_thermal_output_kw)
load_fraction = hp_thermal_kw / max_thermal_output_kw
cop = max(min_cop, nominal_cop - load_cop_penalty * load_fraction)
hp_electric_kw = hp_thermal_kw / cop
backup_kw = min(backup_electric_kw, max(0, thermal_need_kw - hp_thermal_kw))
electrical_kw = hp_electric_kw + backup_kw
```

Fields should include:

```text
max_thermal_output_kw
nominal_cop
min_cop
load_cop_penalty
backup_electric_kw
demand_model
noise_std_pct
```

### AirAirHeatPumpLoadObject

Air-air heat pump COP and capacity should decrease when outdoor temperature decreases.

Required logic:

```text
cop = interpolated temperature COP curve
capacity_factor = interpolated temperature capacity curve
available_thermal_kw = max_thermal_output_kw_at_7c * capacity_factor
hp_thermal_kw = min(thermal_need_kw, available_thermal_kw)
hp_electric_kw = hp_thermal_kw / cop
backup_kw = min(backup_electric_kw, max(0, thermal_need_kw - hp_thermal_kw))
electrical_kw = hp_electric_kw + backup_kw
```

Suggested first COP curve:

```yaml
cop_curve:
  10: 4.5
  0: 3.2
  -10: 2.2
  -20: 1.5
```

Suggested capacity curve:

```yaml
capacity_factor_curve:
  7: 1.0
  0: 0.85
  -10: 0.65
  -20: 0.45
```

Fields should include:

```text
max_thermal_output_kw_at_7c
backup_electric_kw
cop_curve
capacity_factor_curve
demand_model
noise_std_pct
cold_noise_multiplier
```

### AirWaterHeatPumpLoadObject

Air-water heat pump is similar to air-air but typically represents a primary waterborne heating system with clearer electric backup.

Use the same temperature-dependent COP and capacity pattern as air-air, but allow different parameter defaults.

Fields should include:

```text
max_thermal_output_kw_at_7c
backup_electric_kw
cop_curve
capacity_factor_curve
demand_model
noise_std_pct
cold_noise_multiplier
```

### ExhaustAirHeatPumpLoadObject

Exhaust-air heat pump has limited recovered thermal power and often needs substantial electric backup when outdoor temperature is low.

Required logic:

```text
recovered_thermal_kw = min(recovery_thermal_kw, thermal_need_kw)
compressor_kw = recovered_thermal_kw / cop
remaining_thermal_kw = max(0, thermal_need_kw - recovered_thermal_kw)
backup_kw = min(backup_electric_kw, remaining_thermal_kw)
electrical_kw = compressor_kw + backup_kw
```

Fields should include:

```text
recovery_thermal_kw
cop
backup_electric_kw
demand_model
noise_std_pct
```

### PelletStoveLoadObject

Pellet stove thermal output is mainly fuel, but electricity is used for fan/feed/control.

User assumption for first version:

```text
pellet stove uses approximately 0.5 kW electric when running
```

Required first logic:

```text
if thermal_need_kw > running_thermal_need_threshold_kw:
    electrical_kw = electric_kw_when_running
else:
    electrical_kw = 0
```

Fields should include:

```text
electric_kw_when_running = 0.5
running_thermal_need_threshold_kw
thermal_output_kw
demand_model
noise_std_pct
```

P0005 does not need to model pellet fuel consumption, pellet storage or emissions.

## Market proxy distribution

Use first-pass synthetic market proxy weights. These are not official market statistics and must be documented as calibration assumptions.

Suggested weights:

```yaml
heating_type_weights:
  house:
    ground_source_heat_pump: 0.30
    air_water_heat_pump: 0.18
    exhaust_air_heat_pump: 0.12
    direct_electric: 0.20
    air_air_heat_pump: 0.15
    pellet_stove: 0.05

  cabin:
    direct_electric: 0.45
    air_air_heat_pump: 0.35
    pellet_stove: 0.15
    air_water_heat_pump: 0.05

  apartment:
    none: 1.00
```

Implementation should keep these weights configurable, not permanently embedded in factory logic where they cannot be changed.

## Eligibility rules

Initial rules:

```text
apartment sites receive no heating object
house sites receive exactly one primary uncontrolled heating load object
cabin sites receive exactly one primary uncontrolled heating load object
```

Assume no controllable heating assets exist in P0005.

Do not add extra heating elements or supplements yet, but prepare the data model for future roles:

```text
heating_role = primary | supplement | backup
```

P0005 should use:

```text
heating_role = primary
```

## Site size and heat-loss assumptions

Heating demand should depend on `site_type`, `size_class` and `site_random_factor`.

First-pass base design heat-loss values:

```yaml
design_heat_loss_kw:
  house:
    small: 6.0
    medium: 10.0
    large_premium: 16.0
  cabin:
    small: 3.0
    medium: 6.0
    large_premium: 10.0
  apartment:
    small: 2.0
    medium: 4.0
    large_premium: 6.0
```

For P0005 apartments receive no heating object, but apartment defaults may still exist for future use.

Apply:

```text
design_heat_loss_kw = base_design_heat_loss_kw * site_random_factor
```

Suggested balance/design temperatures:

```yaml
house:
  balance_temperature_c: 15.0
  design_temperature_c: -15.0
cabin:
  balance_temperature_c: 10.0
  design_temperature_c: -15.0
apartment:
  balance_temperature_c: 15.0
  design_temperature_c: -15.0
```

Cabins use a lower balance temperature in this first version because occupancy is not yet modelled and winter maintenance heating is a reasonable simplification.

## Expected vs actual

Expected kW should be deterministic for a given context and object.

Actual kW should be based on expected kW plus object-specific stochastic variation.

First approach:

```text
actual_kw = max(0, expected_kw * rng.gauss(1.0, noise_std_pct))
```

For air-source heat pumps, actual volatility should increase when outdoor temperature is below 0°C:

```text
if outdoor_temp_c < 0:
    effective_noise_std_pct = noise_std_pct * cold_noise_multiplier
```

Do not create negative actual kW.

## P0003 integration

P0003 time-series simulation should include heating load objects if they are present in `site.load_objects`.

P0005 must ensure that the simulation context used by the time-series simulator carries outdoor temperature for heating objects.

Possible implementation strategies:

```text
- extend BaseLoadSimulationConfig with a temperature_provider
- or add a HeatingTimeSeriesSimulator wrapper
```

Preferred approach:

```text
Extend the existing base-load time-series simulator so it can optionally use a TemperatureProvider when constructing SimulationContext.
```

If no heating objects are present, P0003 behaviour should remain unchanged.

If heating objects are present and no outdoor temperature is available, the simulator should fail clearly.

## P0004 diagnostics compatibility

No new diagnostics package is required in P0005, but existing P0004 diagnostics should still work because heating objects contribute to aggregate base load.

The annual base-load MWh should materially increase for house and cabin sites when heating objects are included.

## Public-safe requirement

Use only synthetic and neutral assumptions. Do not add company names, real customer data, real prices, real weather data, local database paths or internal commercial terms.

Temperature data from external/local projects may be integrated in a future adapter package, but P0005 must remain self-contained.

## Acceptance criteria

### Demand and weather

- `HeatingDemandModel` exists.
- `thermal_need_kw(outdoor_temp_c)` returns non-negative thermal kW.
- Thermal need increases when outdoor temperature decreases.
- `SimulationContext` can carry `outdoor_temp_c`.
- `TemperatureProvider` abstraction exists.
- `SyntheticTemperatureProvider` exists and can provide outdoor temperature for 2025 timestamps.

### Heating objects

- `DirectElectricHeatingObject` exists and implements the power-first load-object contract.
- `GroundSourceHeatPumpLoadObject` exists and implements the power-first load-object contract.
- `AirAirHeatPumpLoadObject` exists and implements the power-first load-object contract.
- `AirWaterHeatPumpLoadObject` exists and implements the power-first load-object contract.
- `ExhaustAirHeatPumpLoadObject` exists and implements the power-first load-object contract.
- `PelletStoveLoadObject` exists and implements the power-first load-object contract.
- All heating objects return non-negative expected and actual kW.
- Heating object expected kW increases when outdoor temperature decreases, unless capped by max capacity.
- Energy methods derive from kW and `step_hours`.

### Technology behaviour

- Direct electric heating has COP 1.0 behaviour.
- Air-source heat pump COP decreases when outdoor temperature decreases.
- Air-source heat pump capacity decreases when outdoor temperature decreases.
- Air-source heat pumps use electric backup when thermal need exceeds available heat-pump thermal capacity.
- Ground-source heat pump COP decreases mildly under high load.
- Ground-source heat pump uses electric backup when thermal need exceeds heat-pump capacity.
- Exhaust-air heat pump uses limited recovered thermal power and backup for remaining thermal need.
- Pellet stove uses approximately 0.5 kW electric when running.

### Factory and eligibility

- House sites receive exactly one primary uncontrolled heating load object.
- Cabin sites receive exactly one primary uncontrolled heating load object.
- Apartment sites receive no heating object in P0005.
- Heating type weights are configurable.
- Default weights match the P0005 synthetic market proxy assumptions.
- Heating object generation is reproducible with seed.
- Heating objects include `heating_role = primary`.

### Time-series integration

- A default full-year 2025 simulation can run with heating objects and synthetic temperature.
- Site, household and portfolio outputs include heating load through aggregate base-load columns.
- P0004 diagnostics can run on the heating-enriched P0003 result.
- Normal outputs do not expose object-level heating states.

### Boundary

- Heating objects are non-controllable load objects.
- Heating objects do not expose available flexibility, activation, baseline override, rebound, settlement or market logic.
- No real weather database, local file path or external project dependency is hard-coded.

## Out of scope

- Controllable heating assets.
- Heat pump scheduling.
- Rebound or thermal debt.
- Indoor temperature / comfort deficit tracking.
- Occupancy-dependent cabin heating.
- Hybrid primary/supplement systems.
- Extra direct-electric elements for rooms not covered by primary heat.
- Domestic hot water.
- Calibration to real measurement or official market statistics.
- Direct database integration with external weather projects.

## Suggested implementation files

```text
src/flexsimulation/temperature.py
src/flexsimulation/heating_demand.py
src/flexsimulation/heating_load_objects.py
src/flexsimulation/heating_load_factory.py
tests/test_temperature.py
tests/test_heating_demand.py
tests/test_heating_load_objects.py
tests/test_heating_load_factory.py
tests/test_heating_timeseries_integration.py
```

Existing P0003 files may be updated to pass `outdoor_temp_c` into `SimulationContext`.

## Package-run updates required

After implementation, update:

```text
requirements/package-runs/P0005/design.md
requirements/package-runs/P0005/functions.md
requirements/package-runs/P0005/review.md
REPOSITORY_FILES.md
```

Run:

```text
python -m pytest
ruff check .
```
