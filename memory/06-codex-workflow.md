# Codex workflow

All work is package-driven.

## Session bootstrap

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read `memory/bootstrap-manifest.json`.
4. Read files in the manifest `read_order`.
5. Read `REPOSITORY_FILES.md` when path discovery is needed.
6. Read the active package before editing.

## Before code changes

Write a short consistency review covering:

- active package id,
- files expected to change,
- observation-boundary impact,
- business-case impact,
- tests required.

## During implementation

- Keep examples synthetic.
- Avoid leakage from latent state to observations.
- Update `REPOSITORY_FILES.md` when paths are added, removed or moved.
- Add or update tests with every behaviour change.

## Package-run evidence

When implementing a package, store design, functions, findings and review notes under:

```text
requirements/package-runs/Pxxxx/
```
