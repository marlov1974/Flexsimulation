# P0002 Functions

## Added or changed functions

To be completed during implementation.

## Public interfaces expected

- Stock generator for households and sites.
- Base-load object factory for initial load objects.
- Base-load object method contract:
  - `expected_kwh(context)`
  - `actual_kwh(context, rng)`

## Data contracts

- Household has `persons_count`, not `persons_class`.
- Site has `site_type`, `site_role`, `size_class`, `site_random_factor`.
- Base-load objects are latent/debug.

## Test coverage

To be completed during implementation.
