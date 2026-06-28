# Flexsimulation

Source-of-truth modelling repository for an interactive executive business-case simulator for distributed flexibility and virtual-battery capability value.

The purpose is to replace static presentation and spreadsheet-style business cases with a polished interactive page where decision makers can explore how capability choices, ownership models, optimisation scope and market integration change profitability, risk, customer value and strategic control.

The intended outcome is that users discover, through interaction, that local asset-by-asset flexibility initiatives can look attractive in isolation while destroying or hiding system value. The simulator should show why shared system capabilities such as common data models, 15-minute plans, baseline management, stacked optimisation, cross-asset portfolio effects, rebound scheduling, wholesale/imbalance integration and value attribution are critical to real profitability.

## Strategic problem

Fragmented local flexibility initiatives can create false-positive business cases. A local initiative may show attractive gross revenue for one resource type while leaving important system effects outside the calculation boundary.

Common fragmentation patterns the simulator should make visible:

- EV charging solutions limited to a subset of vehicle brands or charging partners.
- Solar solutions optimised locally with one partner.
- Battery solutions optimised locally with another partner.
- Flexibility bids sent to ancillary markets without integration to wholesale position management.
- Imbalance costs hidden, ignored or attributed to another team.
- Rebound energy treated as a side effect instead of a scheduled and traded portfolio position.
- Assets optimised locally without connection to the household residual load profile.
- Energy sharing treated as an administrative problem instead of a product and portfolio opportunity.
- Partner revenue-share models optimising gross activation revenue rather than net portfolio value.

The simulator should compare local/gross business-case views with integrated/net system views.

## Customer value thesis

A well-designed integrated system should create value for both the portfolio owner and the customer.

The customer should experience the product as a growing energy system rather than a set of disconnected devices. Each new asset or capability should make the whole system better: lower cost, better use of local production, smarter charging, better comfort protection, higher flexibility bonus and a clearer path to the next upgrade.

The simulator should therefore include customer value and customer progression effects, not only internal market revenue. Examples:

- customer savings,
- flexibility bonus,
- energy-sharing value,
- comfort and target-state protection,
- next-best-upgrade value,
- system maturity score,
- retention or stickiness effect.

## Mandatory AI bootstrap

For every new AI/chat/Codex session working on this repository:

1. Read this `README.md`.
2. Read `AGENTS.md`.
3. Read `memory/bootstrap-manifest.json`.
4. Read every file listed in the manifest `read_order`, in order.
5. Read `REPOSITORY_FILES.md` as the tracked path index when file discovery is needed, when planning source/package inspection, or when a task may add, remove or move tracked files.
6. Treat `REPOSITORY_FILES.md` as a catalog, not as a command to read every tracked file during ordinary bootstrap.
7. Read the active package in `requirements/packages/` before editing.
8. If any mandatory read fails, stop and report `BOOTSTRAP FAILED` with the missing file/step.

## Repository boundary

This repository may contain:

- generic virtual-battery concepts,
- synthetic household, asset and market assumptions,
- synthetic prices, weather, activation events and customer segments,
- capability definitions,
- prototype simulator code,
- non-confidential design notes.

This repository must not contain:

- real customer information,
- real commercial terms,
- real internal product names,
- real counterparties or business unit names,
- real production system names,
- real price curves or transaction extracts,
- copied internal documents,
- company-specific strategy text or company names.

Use neutral vocabulary such as:

```text
household
site
home site
cabin site
energy channel
baseline plan
activation plan
rebound position
virtual battery portfolio
market scenario
business-case scenario
local initiative
system capability
edge capability
portfolio owner
customer value
```

## Layout

```text
memory/        durable solution understanding
requirements/ ordered capability/package work
docs/          durable model and business-case documentation
configs/       synthetic scenario and segment assumptions
src/           simulator prototype source code
web/           interactive executive playground, future
outputs/       generated outputs, gitignored except .gitkeep
tests/         unit tests and fixtures
```

Tracked repository paths are listed in `REPOSITORY_FILES.md`. When a change adds, removes or moves tracked files, keep `REPOSITORY_FILES.md` synchronized in the same change.

## Package model

All implementation work is package-driven.

A package is an ordered whole-solution change version:

```text
P0001, P0002, P0003, ...
```

Every code change must reference exactly one package id. Rollback is also a new forward-moving package.

Current bootstrap package:

```text
requirements/packages/P0001-bootstrap-flexsimulation-repo.md
```

## Core modelling principle

The simulator is a synthetic reality proxy. It may contain latent household, person, device and behaviour states, but ML/bidding models must only observe configured energy channels and controller plans through an observation layer.

The first observation boundary is household-level 15-minute data:

```text
total_power_kw
pv_power_kw
ev_power_kw
heatpump_power_kw
battery_power_kw
planned_total_power_kw
planned_pv_power_kw
planned_ev_power_kw
planned_heatpump_power_kw
planned_battery_power_kw
```

Sign convention:

```text
+ means electricity consumption/load
- means generation/export/discharge
```

## First modelling goal

The first simulator goal is not physical accuracy for its own sake. The first goal is to compare business-case scenarios:

```text
S0_fragmented_no_coordination
S1_local_smart_optimisation
S2_dual_home_integrated_optimisation
S3_portfolio_virtual_battery
S4_full_market_optimizer
```

The main output should be incremental value, for example SEK/customer/year, system value uplift, customer value uplift and strategic control, not only MW.
