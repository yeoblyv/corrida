# Contributing

How we work in this repo. The git commands for all of this are in
[docs/git-cheatsheet.md](docs/git-cheatsheet.md).

## Branches

- Everyone works on their own branch: `mark`, `Marjan`, `Daniel`, `yehor`.
  A short `feat/<topic>` branch is fine for work that isn't one person's.
- `main` should always build. Code gets into `main` through a pull
  request, never by pushing to it directly.
- Don't rewrite the history of `main` (no `--amend` with a force-push, no
  rebase). If something is wrong, fix it with a new commit.
- Merge `main` into your branch before you open a pull request, so
  conflicts are solved on your branch.

## Commits

- Start the message with a
  [Conventional Commits](https://www.conventionalcommits.org/) type:
  `feat:`, `fix:`, `docs:`, `test:`, `chore:` or `refactor:`. Write it in
  English, in the imperative, without a period at the end. A scope like
  `feat(navigation):` is fine too.
  - Good: `feat: add wall-following state machine`
  - Bad: `fix 123`, `update stuff`
- One change per commit. Commit when a piece of work is done, don't leave
  a day of work uncommitted.

## Pull requests

Pull requests are for code: `src/`, `scripts/`, `notebooks/`, `tests/`.
Docs and repo files (`README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `docs/`,
the license files) can go straight to `main`. Yehor does that as the
GitHub role from
[ADR-0001](docs/adr/0001-team-roles-and-working-agreement.md). This is
only for docs, not for code.

Nobody has to review your pull request, you can merge it yourself. We
trust each other to only merge what was really tested. Before you merge:

1. Build it (`colcon build`) and run it, on the robot or in simulation.
2. Run `./scripts/lint.sh`. There is no CI, so nothing else checks this.
3. Solve the conflicts with `main` on your branch.
4. Write in the pull request what you tested and how, for example "ran on
   the Create 3 in the hallway maze, 3 of 3 runs OK".

Keep pull requests small: one node or one launch file, not a whole week
of work.

## Code

- Python, formatted with `black` and checked with `ruff` (settings in
  `pyproject.toml`). Run `./scripts/lint.sh` before you push.
- Type hints on functions, and a short docstring where it isn't obvious
  what something does.
- ROS 2 names: packages are called `corrida_<name>`, nodes and topics use
  `snake_case`.
- No commented-out code. Git keeps the old versions.

## Tests

- Logic that works without ROS and the robot (maze solving, filtering,
  coordinate maths) gets a `pytest` test in `tests/`.
- Nodes that only make sense on the robot or in a simulator are tested by
  hand. Say how in the pull request.

## Notebooks

Jupyter notebooks go in `notebooks/`:

- `demos/` - finished notebooks that show something working, with their
  outputs kept. Good material for the report and the presentations.
- `exploration/` - trying something out before it becomes code in `src/`.
- `cheatsheets/` - notes with examples you can run.

A notebook starts with a Markdown cell that says what it does and what it
needs to run. Code that has to run on the robot belongs in `src/`, a
notebook is not enough. Clear big outputs in `exploration/` before you
commit.

## What not to commit

Build output (`build/`, `install/`, `log/`), virtual environments, editor
files, VM images and anything secret (passwords, tokens, Wi-Fi
credentials). `.gitignore` covers most of it. After `git add .`, check
`git status` before you commit.

## Docs

- Planning and meeting minutes are in Microsoft Teams, not here (agreed
  in the first meeting).
- `docs/adr/` has one short file per bigger decision, like the team roles
  and the license. Start from `docs/adr/TEMPLATE.md`. An accepted decision
  isn't edited afterwards, a new one replaces it.
- `docs/REFERENCES.md` has the reference list and how we cite.

## Sources

We cite in APA 7, the style Hanze uses. The details and the reference
list are in [docs/REFERENCES.md](docs/REFERENCES.md). The report is the
exception: the assignment asks for IEEE format, so it uses IEEE numbered
references.

- A fact from outside the repo (a deadline, a spec, a number from a
  datasheet) gets its source next to it.
- Code that was taken or adapted from somewhere (a tutorial, the ROS
  docs, a GitHub repo, Stack Overflow) gets a comment with the link at
  that code, and the source goes into the reference list:

  ```python
  # reading the bag like in the rosbags docs: https://ternaris.gitlab.io/rosbags/topics/highlevel.html
  ```

- Code you wrote yourself doesn't need a source.

The same goes for anything an AI assistant helped with, see
[AGENTS.md](AGENTS.md).
