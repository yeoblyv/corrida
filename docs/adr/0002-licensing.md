# ADR-0002: License the repository, split by content type

**Status:** Accepted
**Date:** 2026-09-14

## Context

The repository is currently private, with the possibility of making it
public once the project is submitted, defended, and graded. Once
public, other students on this or a future run of the same course may
find and read it - the academic-integrity note in `LICENSE-DOCS` (below)
addresses that.

Source code and written material (the IEEE report, documentation) have
different licensing conventions, and Creative Commons explicitly advises
against using its licenses for software.

## Decision

Two licenses, applied to different parts of the repository:

- **MIT** ([LICENSE](../../LICENSE)) - `src/`, `scripts/`, `notebooks/`,
  `tests/`. Permissive, requires preserving the copyright/license notice
  in copies.
- **CC BY 4.0** ([LICENSE-DOCS](../../LICENSE-DOCS)) - `IEEE/` and
  `docs/`, except `docs/course-materials/` (the course's own material,
  not ours to license - stays cited as personal communication per
  `docs/REFERENCES.md` §4, not relicensed).

`LICENSE-DOCS` states explicitly that a license here governs copyright,
not Hanze's academic integrity policy - it does not authorize another
student using this work to satisfy their own coursework for this or an
equivalent assignment. That distinction is spelled out in the file
itself, not only here, so anyone finding the repository sees it.

## Consequences

Gains: the repository is ready to be made public without an ad hoc
licensing scramble later; both licenses require attribution, so anyone
reusing this work has to credit the people who made it; the
academic-integrity caveat is attached directly to the grant, not left
implicit.

Costs: a split license is one more thing a reader has to understand
before reusing anything; mitigated by stating it plainly in
`LICENSE-DOCS` and pointing to both files from `README.md`.

This ADR does not itself make the repository public - that remains a
separate decision.
