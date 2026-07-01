# Package runs

Package-run evidence stores design, functions, findings, review notes and execution evidence for each package.

Use one folder per package:

```text
requirements/package-runs/P0001/
requirements/package-runs/P0002/
requirements/package-runs/P0003/
```

## Required files

Every implementation package must maintain these files:

```text
design.md
functions.md
findings.md
review.md
```

A package is not complete until all four files are updated.

## File responsibilities

### `design.md`

Use this before and during implementation. It should explain the goal, assumptions, selected design, alternatives considered, boundaries, expected file changes and tests.

### `functions.md`

Use this to document what changed in the implementation surface: classes, functions, public interfaces, data contracts, invariants and test coverage mapping.

### `findings.md`

Use this to document lessons and discoveries during implementation: model findings, technical findings, bugs found, mismatches with requirements, tradeoffs and follow-up candidates.

### `review.md`

Use this at package completion. It should document acceptance-criteria status, tests run, lint/static checks, files changed, risks, follow-up and whether the package is complete.

## Rules

- Keep package-run evidence neutral and public-safe.
- Do not include real customer data, company names, real prices, local paths, screenshots or proprietary exports.
- Link every implementation change to exactly one package id.
- Update `REPOSITORY_FILES.md` when tracked files are added, removed or moved.
- If a package touches simulator observations, explicitly document how latent state remains protected.
- If a package changes modelling assumptions, document them in `findings.md` and `review.md`.
