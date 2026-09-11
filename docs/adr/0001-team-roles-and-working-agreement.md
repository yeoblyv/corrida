# ADR-0001: Team roles and shared ownership of development

**Status:** Accepted
**Date:** 2026-09-11

## Context

A four-person team needs a clear point of contact for each recurring
concern - talking to tutors, sequencing day-to-day work, keeping the
repository/documentation/report to a standard, and researching the
problem domain - so that none of these default to "whoever notices
first." At the same time, the team wants to avoid a hierarchy that lets
role labels substitute for actually building the robot software
together.

## Decision

Each member holds a primary area of accountability, on top of - not
instead of - equal participation in building the software:

- **Project lead** - strategic decisions, organizational coordination,
  primary point of contact with tutors and stakeholders.
- **Tactical planning** - day-to-day task sequencing and prioritization;
  shares communication duties with the project lead.
- **Repository & standards** - owns the repository (structure, git
  workflow, `CONTRIBUTING.md`, `AGENTS.md`, the citation standard), the
  IEEE report's process and formatting, and technical support across
  both hardware and software.
- **Research** - investigates the problem domain and prior art; shares
  communication duties, and holds standing physical access to the robot
  for hands-on testing at any time.

Current holders are recorded in `README.md`'s team section, not here -
this ADR records the *role structure and its intent*, so it doesn't need
a new revision every time a person changes seats.

Every member is expected to contribute to the actual software roughly
equally. The roles above assign accountability for a concern, not
exclusive rights to a part of the work - they don't gate who is allowed
to write code, touch the robot, or make a technical call.

## Consequences

Gains: a named owner for organizational, tactical, documentation/support,
and research concerns; a standing answer to "who do I ask about X"
without waiting on the whole team.

Costs: role labels can calcify into a hierarchy if nobody actively
guards against it. If contribution to the codebase becomes visibly
uneven along role lines instead of staying roughly equal as intended,
that's a signal to revisit this agreement - with a new ADR that
supersedes this one, not a silent drift.
