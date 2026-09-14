# ADR-0001: Team roles and shared ownership of development

**Status:** Accepted
**Date:** 2026-09-11

## Context

At the team's first meeting (2026-09-11), roles were assigned so each
recurring concern - leading the team, planning, communication, keeping
minutes, the report, the repository, presenting - has a named owner
instead of defaulting to "whoever notices first." Programming stays a
shared effort; the role split doesn't gate it.

## Decision

Each member holds a named role, on top of - not instead of - equal
participation in building the software:

- **Leader (Mark)** - overall direction for the team.
- **Planning & communication (Marjan)** - day-to-day task sequencing and
  the team's main point of contact.
- **Meeting minutes (Daniel)** - keeps the record of what was decided at
  each meeting.
- **GitHub (Yehor)** - owns the repository: structure, git workflow,
  `CONTRIBUTING.md`/`AGENTS.md`, the citation standard.
- **Report** - everyone writes their own section on their own progress;
  Yehor compiles the final version.
- **Programming** - everyone contributes; how the work splits is decided
  as the project moves into implementation.
- **Presentation** - everyone presents the part they made.

Current holders are recorded in `README.md`'s team section, not here -
this ADR records the *role structure*, so it doesn't need a new revision
every time a person changes seats.

Every member is expected to contribute to the actual software roughly
equally. The roles above assign accountability for a concern, not
exclusive rights to a part of the work - they don't gate who is allowed
to write code, touch the robot, or make a technical call.

## Consequences

Gains: a named owner for leadership, planning/communication, minutes,
and the repository; a standing answer to "who do I ask about X" without
waiting on the whole team.

Costs: role labels can calcify into a hierarchy if nobody actively
guards against it. If contribution to the codebase becomes visibly
uneven along role lines instead of staying roughly equal as intended,
that's a signal to revisit this agreement - with a new ADR that
supersedes this one, not a silent drift.
