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
7. Write a short consistency review before code changes.

## Rules

- Use generic terms only.
- Do not store sensitive business material.
- Every implementation change should reference one package id.
- Keep `REPOSITORY_FILES.md` synchronized when tracked paths change.
- Do not expose latent simulator state to ML/bidding interfaces.
- Treat business-case scenario comparison as a first-class simulator output.

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