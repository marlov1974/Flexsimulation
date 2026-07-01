# P0005 Functions

## Added or changed functions

To be completed during implementation.

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

## Test coverage

To be completed during implementation.
