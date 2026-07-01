# AGENTS.md

Read `README.md` before changing files.

This repository is a generic modelling prototype for virtual-battery capability and business-case simulation. Keep examples synthetic and names neutral.

## Before editing

1. Sync local repo.
2. Read `README.md`.
3. Read `AGENTS.md`.
4. Read `memory/bootstrap-manifest.json` and every file in `read_order`.
5. Read `REPOSITORY_FILES.md` when path discovery is needed.
6. Read the active package before implementation.
7. Write a short consistency review in the active package-run `design.md` before code changes.

## Rules

- Use generic terms only.
- Do not store sensitive business material.
- Every implementation change should reference one package id.
- Keep `REPOSITORY_FILES.md` synchronized when tracked paths change.
- Do not expose latent simulator state to ML/bidding interfaces.
- Treat business-case scenario comparison as a first-class simulator output.
- Every implementation package must update package-run evidence before it can be considered complete.

## Mandatory package-run evidence

For every implementation package, maintain this folder:

```text
requirements/package-runs/Pxxxx/
  design.md
  functions.md
  findings.md
  review.md
```

The package is not complete until all four files are updated.

### `design.md`

Document before and during implementation:

- goal,
- consistency review,
- assumptions,
- selected design,
- alternatives considered and rejected,
- boundaries to other packages,
- expected files and tests.

### `functions.md`

Document implemented interfaces:

- new or changed classes,
- new or changed functions,
- public interfaces,
- data contracts,
- important invariants,
- compatibility notes,
- test coverage mapping.

### `findings.md`

Document learning during implementation:

- modelling findings,
- technical findings,
- bugs or mismatches found,
- tradeoffs made,
- assumptions that should be revisited,
- follow-up candidates for later packages.

### `review.md`

Document completion evidence:

- implementation summary,
- acceptance-criteria status,
- tests run,
- lint/static checks run,
- files changed,
- risks and follow-up,
- clear statement whether the package is complete.

## Preferred terms

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
capability
system capability
edge capability
```
