# P0002 Functions

## Added or changed functions

- `generate_households(seed, config)` creates reproducible synthetic households and sites.
- `with_site_load_objects(households, load_objects_by_site_id)` attaches latent load objects to sites.
- `generate_base_load_objects_for_site(site, rng)` creates initial base-load objects for one site.
- `generate_base_load_objects_for_sites(sites, seed)` creates base-load objects keyed by site id.
- `generate_synthetic_stock(seed, config)` creates households, sites and latent base-load objects.
- `summarize_stock(households)` returns a debug summary of generated stock.

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
- Base-load objects implement `expected_kwh(context)` and `actual_kwh(context, rng)`.
- Default timestep context uses `step_hours = 0.25`.

## Test coverage

- Reproducible household and site generation.
- Valid site configuration mapping.
- Absence of `persons_class`.
- Base-load object count rules.
- Non-negative expected and actual kWh.
- Cold appliance cycling.
- Stochastic light and towel-rail behaviour.
- Stock summary debug output.
