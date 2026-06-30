# P0002 Synthetic stock and base-load object generator

## Purpose

Create the first executable population foundation for the simulator.

This package must generate a small synthetic household stock and attach initial base-load objects to each simulated site. It does not need to run a full time-series simulation yet. The goal is to create the synthetic reality structure that later batch simulation packages can tick through at 15-minute resolution.

## Business intent

The package supports the first residual-load simulation capability. It creates a realistic-enough synthetic stock where base consumption can later be simulated from object-level loads such as cold appliances, internet equipment, standby clusters, always-on lighting and towel rails.

This matters because base load:

- consumes local production,
- uses battery energy,
- creates residual-load forecast uncertainty,
- reduces risk-adjusted bidable flexibility,
- differs materially by site type, site size and household size.

## Scope

Implement two foundations:

```text
1. Synthetic stock generation
2. Base-load object generation
```

Full 15-minute batch simulation is out of scope for this package except for simple smoke tests of object methods.

## Core concepts

### Household

A household is the customer-level synthetic entity.

Required fields:

```text
household_id
persons_count
site_configuration
sites
```

`persons_count` is an integer sampled from 2 to 5. Do not use `persons_class`.

Default family-heavy distribution:

```yaml
persons_count_weights:
  2: 0.15
  3: 0.25
  4: 0.35
  5: 0.25
```

### Site configuration

Each household receives one weighted site configuration.

Initial supported configurations:

```text
apartment_only
house_only
cabin_only
apartment_plus_cabin
house_plus_cabin
```

The weights must be configurable. A neutral default can be used, but the implementation must not hard-code the scenario permanently.

### Site

A site is a simulated electricity location. A household can have one or more sites.

Required fields:

```text
site_id
household_id
site_role
site_type
size_class
persons_count
site_random_factor
load_objects
asset_objects
```

Initial `site_role` values:

```text
primary_home
cabin
```

Initial `site_type` values:

```text
apartment
house
cabin
```

Initial `size_class` values:

```text
small
medium
large_premium
```

`site_random_factor` is a permanent site-specific factor used later to create variation within the same segment. It must be sampled reproducibly and clamped to configured bounds.

## Site size sampling

Site size must be sampled from configurable weights by `site_type` and adjusted by `persons_count`.

Example intent:

- 2-person households are more likely to have small or medium sites.
- 4- and 5-person households are more likely to have medium or large/premium sites.
- Small apartment with many persons should be rare but not impossible unless excluded in config.
- Large/premium home should make larger cabin more likely in plus-cabin configurations.

The exact first implementation can be simple, but the sampling must be weighted and reproducible.

## Base-load object generation

Each site receives initial base-load objects based on:

```text
site_type
size_class
persons_count
```

Base-load objects are latent simulation objects. They must not be exposed as ML observations. Later observation layers may expose only aggregate residual or aggregate energy channels.

### Initial base-load object types

Implement these initial object types:

```text
ColdApplianceObject
InternetObject
StandbyClusterObject
AlwaysLightObject
TowelRailObject
```

### ColdApplianceObject

Represents one cold appliance.

Fields:

```text
object_id
household_id
site_id
subtype
rated_kw
duty_cycle
cycle_length_steps
phase_offset
```

Supported `subtype` values:

```text
fridge
freezer
fridge_freezer
```

Creation rule:

```text
Each site gets 1-3 cold appliance objects.
```

The mix should depend on site type and size. A simple first rule is acceptable:

```text
1 unit  -> fridge_freezer
2 units -> fridge + freezer
3 units -> fridge + freezer + freezer
```

The object should be able to return expected and actual kWh for a timestep. Actual kWh may be cyclic using `duty_cycle`, `cycle_length_steps` and `phase_offset`.

### InternetObject

Represents one always-on internet/network unit such as router, access point, switch or modem.

Fields:

```text
object_id
household_id
site_id
kw
noise_std_pct
```

Creation rule:

```text
Each site gets 1-3 internet objects.
```

Larger/premium sites should tend to receive more internet objects than small sites.

### StandbyClusterObject

Represents a cluster of standby equipment.

Fields:

```text
object_id
household_id
site_id
cluster_type
unit_count
watt_per_unit
noise_std_pct
```

Rules:

```text
Each StandbyClusterObject represents 2 standby units.
Home sites receive site-level standby clusters based on size.
Home sites receive one person-level standby cluster per person.
Cabin sites receive site-level standby clusters based on size and optional cabin-extra clusters.
```

Initial `cluster_type` values:

```text
site
person
cabin_extra
```

For example, a home site with 4 persons and 2 site clusters receives:

```text
2 site clusters + 4 person clusters = 6 StandbyClusterObjects = 12 standby units
```

### AlwaysLightObject

Represents one 50 W light that is often on, but still random.

Fields:

```text
object_id
household_id
site_id
kw = 0.05
on_probability_per_step
```

Creation rule:

```text
Each site gets 1-3 AlwaysLightObject instances.
```

Larger/premium sites should tend to receive more always-on lights.

### TowelRailObject

Represents one towel rail.

Fields:

```text
object_id
household_id
site_id
kw
on_probability_per_step
```

Creation rule:

```text
Each site gets 0-2 TowelRailObject instances.
```

Larger homes and large/premium sites should tend to receive more towel rails than small sites. Cabin sites may have towel rails but should not always have them.

## Object method contract

Every base-load object must provide:

```python
expected_kwh(context) -> float
actual_kwh(context, rng) -> float
```

The object does not need to implement market, plan, activation or rebound behaviour in this package.

All base-load objects are non-controllable load objects.

## Simulation context

Create a minimal context object if needed.

Required information:

```text
timestep
step_hours
```

Default `step_hours` should be `0.25` for a 15-minute timestep.

## Output and debug

The package should support a debug summary of generated stock:

- number of households,
- number of sites by site type,
- number of sites by size,
- persons_count distribution,
- object counts by type,
- average object count per site.

It is acceptable to implement this as a Python function returning a dictionary. CSV export can be added later.

## Public-safe requirement

Use only synthetic and neutral examples. Do not add company names, real customer data, real prices or internal commercial terms.

## Acceptance criteria

### Stock generation

- Generate configurable `N` households. Default for this package: `100`.
- `persons_count` is always one of `2, 3, 4, 5`.
- Default `persons_count` weights are `0.15, 0.25, 0.35, 0.25` for 2, 3, 4 and 5 persons.
- No `persons_class` field exists.
- Each household has one valid `site_configuration`.
- Supported configurations are `apartment_only`, `house_only`, `cabin_only`, `apartment_plus_cabin`, `house_plus_cabin`.
- Every household has at least one site.
- `apartment_only` creates one apartment primary-home site.
- `house_only` creates one house primary-home site.
- `cabin_only` creates one cabin site.
- `apartment_plus_cabin` creates one apartment primary-home site and one cabin site.
- `house_plus_cabin` creates one house primary-home site and one cabin site.
- Site size is one of `small`, `medium`, `large_premium`.
- Same seed produces the same household and site stock.

### Base-load object generation

- Every site receives 1-3 `ColdApplianceObject` instances.
- Every cold appliance subtype is one of `fridge`, `freezer`, `fridge_freezer`.
- Every site receives 1-3 `InternetObject` instances.
- Every home site receives site standby clusters and one person standby cluster per person.
- Cabin sites receive site standby clusters and optional cabin-extra standby clusters.
- Every `StandbyClusterObject` represents exactly 2 standby units.
- Every site receives 1-3 `AlwaysLightObject` instances.
- Every `AlwaysLightObject` has `kw = 0.05`.
- Every site receives 0-2 `TowelRailObject` instances.
- Larger/premium sites tend to receive more internet, always-light and towel-rail objects than small sites.
- More persons create more person standby clusters on home sites.
- Object stock is reproducible with seed.

### Object methods

- All base-load objects return non-negative `expected_kwh`.
- All base-load objects return non-negative `actual_kwh`.
- Cold appliance actual values vary over timesteps when cycle parameters imply on/off cycling.
- Internet and standby objects are near-constant with small noise.
- Always-light objects are usually on but not guaranteed every timestep.
- Towel rail objects are stochastic based on `on_probability_per_step`.

### Boundary

- Generated object-level details are latent/debug data.
- No ML observation object should expose individual cold appliance, internet, standby, lighting or towel-rail object states in this package.

## Out of scope

- Full 15-minute multi-day batch simulation.
- Behavioural load events such as cooking, shower, laundry or occupancy.
- Assets such as PV, battery, EV charger or controllable heat pump.
- Market bidding, activation, rebound or settlement.
- Interactive web page.

## Suggested implementation files

```text
src/flexsimulation/population.py
src/flexsimulation/base_load_objects.py
src/flexsimulation/stock_generator.py
src/flexsimulation/base_load_factory.py
tests/test_population.py
tests/test_base_load_objects.py
tests/test_base_load_factory.py
```

Existing files may be refactored if needed, but keep the package focused.
