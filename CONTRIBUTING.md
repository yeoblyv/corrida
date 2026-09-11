# Contributing

Working agreement for Corrida Team on the Introduction Project. Covers how we branch, commit, review, and ship code and
documentation. Hardware summary and team roster live in `README.md`;
technical and organizational decisions live in `docs/adr/`; the workshop's ROS2/Jazzy
environment and AI-assistants behavior are defined in `AGENTS.md`; the
citation standard every fact and adapted line of code follows is
[docs/REFERENCES.md](docs/REFERENCES.md) (§9 below).

## 1. Deadlines (drive everything below)

| Date | Deliverable | Graded | Format |
| --- | --- | --- | --- |
| 2026-09-20 | Individual learning goals + plan | No | 1 page, Brightspace |
| 2026-09-29 | Group progress presentation | No | Live |
| 2026-10-20 | Group demonstration (maze run) | Yes | Live, 8+8 min |
| 2026-10-25 | Group report/paper | Yes | IEEE format, max 6 pages |
| 2026-11-02 | Individual reflection | No | 1 page, Brightspace |

Per E. Bergsma, F. N. Martins, & F. J. Guzman (personal communication,
September 11, 2026, slide 3) - see [docs/REFERENCES.md](docs/REFERENCES.md)
for the citation standard and [docs/course-materials/](docs/course-materials/)
for the archived slides. If Brightspace ever states a different date,
Brightspace wins.

## 2. Branching

- `main` is always buildable and demo-able - never push straight to it.
- Each member works on a personal branch (`yehor`, `marjan`, `daniel`,
  `mark`) or a short-lived `feat/<topic>` branch for a self-contained chunk
  of work that doesn't map to one person.
- Bring `main` into your branch before opening a PR (merge or rebase), so
  conflicts get resolved on your branch, not on `main`.
- Exact commands (clone, create your branch, pull before pushing, open a
  PR, set up a new machine/VM) are in
  [docs/git-cheatsheet.md](docs/git-cheatsheet.md).

## 3. Commits

- [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.
  Imperative mood, no trailing period, English only.
  - Good: `feat(navigation): add wall-following state machine`
  - Bad: `fix 123`, `update stuff`
- One logical change per commit. Commit at the end of each working session
  or completed sub-task - don't let a day of work sit uncommitted.

## 4. Pull requests & review

Every merge into `main` goes through a PR - no direct pushes to `main`.
No mandatory review: you can merge your own PR once it's ready, nobody
has to sign off first. This runs on trust, not enforcement - there's no
consequence built in if someone merges something they didn't actually
test, only a team that has to live with a broken `main`.

A PR is ready to merge when:

1. You've actually run it - built (`colcon build`) and exercised it on
   hardware or in simulation, not just read the diff.
2. Lint is clean, checked locally (`./scripts/lint.sh`) - the repo is
   private, so there is no CI to catch this for you.
3. All conflicts with `main` are resolved on the feature branch.
4. The PR description states what you tested and how (e.g. "ran on the
   Create 3 in the hallway maze, 3/3 successful attempts") - this is
   your statement that points 1-3 above are actually true, since nobody
   else is checking.

Keep PRs small enough that point 4's description stays honestly
specific - not "all of this week's work."

## 5. Code style

- Python, PEP 8, enforced by `ruff` + `black` (config in `pyproject.toml`).
  Run `./scripts/lint.sh` before pushing - there's no CI to run it for
  you.
- Type hints on public functions; a docstring on every node, class, and
  non-trivial function - one-line summary plus *why* it exists if that's
  not obvious, never a restatement of the signature.
- ROS2 conventions: package names `snake_case` prefixed `corrida_`, node
  names `snake_case`, topics `/lower_case_with_slashes`.
- No dead or commented-out code - git history is the history.

## 6. Tests

- Logic that doesn't need ROS2 or the physical robot (maze-solving
  algorithm, sensor filtering, coordinate transforms) gets a `pytest` unit
  test under `tests/`.
- Nodes that only make sense wired to the robot or a simulator are
  verified manually before merging; say how you verified it in the PR
  description.

## 7. Repository hygiene

- Never commit: build artifacts (`build/`, `install/`, `log/`), virtual
  environments, `.pyc` files, editor/OS files, secrets, Wi-Fi credentials,
  or VM images - see `.gitignore`. `vms/` is a local/shared-drive-only
  working folder and is git-ignored on purpose: VM snapshots run into
  gigabytes and Git is not built for that.
- If you used `git add .` or `git add -A`, check `git status` before
  committing - confirm nothing unexpected got staged.

## 8. Documentation

- `docs/adr/` - one file per non-trivial technical or organizational
  decision (ROS2 distro, planning algorithm, LiDAR driver choice, team
  roles), from `docs/adr/TEMPLATE.md`. Numbered sequentially, never
  edited after acceptance - a changed decision is a new ADR that
  supersedes the old one.
- `docs/learning-goals/` and `docs/meeting-notes/` - individual and team
  notes tied to the dates in §1.
- `docs/course-materials/` - original course documents (kickoff slides,
  assignment sheets, rubrics), archived as a practical copy. Cite them as
  personal communication per `docs/REFERENCES.md` §4, not as a reference
  list entry - see §9.
- `docs/REFERENCES.md` - the repo's single citation standard (APA 7th,
  per Hanze's library guide) and bibliography. Read this before citing
  anything.
- `IEEE/` - the report draft. One current draft, versioned by git history,
  not by filename suffixes.

## 9. Source attribution

One standard, repo-wide: **APA, 7th edition**, per Hanze's own library
guide - full policy, in-text formats, and the bibliography itself live in
[docs/REFERENCES.md](docs/REFERENCES.md). This section says where it
applies; that file says how to do it. Applies to every contributor, human
or AI (see [AGENTS.md](AGENTS.md)), and to every artifact - docs, code
comments, commit messages - with one exception: the report in `IEEE/`
uses IEEE's own numbered citation style instead (see `IEEE/README.md`).

- **A fact taken from outside this repo** (a deadline, a hardware spec, a
  grading rule, a number from a paper) gets an in-text citation
  (`docs/REFERENCES.md` §2) next to it, pointing at a full entry in
  `docs/REFERENCES.md` §5, or - for undistributed course material like
  lecture slides - the personal-communication form in §4. "It's on
  Brightspace" is not a citation.
- **Code adapted from an external source** (an official ROS 2/Create
  3/Foxglove tutorial, a GitHub repo, a Stack Overflow answer, any
  tutorial snippet) carries a comment or docstring with the source URL,
  directly on the adapted code - not only in the commit message, which
  git history can lose track of relative to the line it justifies - *and*
  gets a matching entry in `docs/REFERENCES.md` §5, formatted per §3's
  software/documentation template:

  ```python
  def normalize_scan(scan: LaserScan) -> list[float]:
      """Replace inf/nan LiDAR ranges with the sensor's max range.

      Adapted from the ROS 2 Jazzy sensor_msgs/LaserScan tutorial:
      https://docs.ros.org/en/jazzy/Tutorials/...
      (full citation: docs/REFERENCES.md)
      """
  ```

  A short inline comment (`# Source: <url>, see docs/REFERENCES.md`) is
  fine when a docstring would be overkill for a few adapted lines.
- Code written from scratch, or so standard it has no single source
  (a for-loop, a basic ROS2 publisher boilerplate you've internalized),
  needs no citation - this rule is for content that came *from*
  somewhere specific, not a blanket citation requirement on all code.

## 10. Definition of done (per PR)

- [ ] Builds clean (`colcon build`).
- [ ] Lint clean, checked locally (`./scripts/lint.sh`).
- [ ] New/changed logic has a test where it's testable outside the robot.
- [ ] No secrets, VM images, or build artifacts staged.
- [ ] Facts and adapted code carry source attribution per §9.
- [ ] PR description states what was tested and how - self-certified,
      no review gate (§4).
- [ ] Commit messages follow §3.
