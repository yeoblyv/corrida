# scripts/

Team-wide setup/build/lint helpers.

- `build.sh` — `colcon build` the workspace (requires ROS2 already sourced).
- `lint.sh` — run `ruff` + `black --check` before every push. The repo is
  private, so there's no CI to catch violations for you.
- `env.sh` — `source scripts/env.sh` sets up ROS 2 Jazzy, `ROS_DOMAIN_ID`
  (default 10), `ROBOT_NAMESPACE` (default `/robot_10`, used by launch files as the node namespace) and this workspace's overlay. Use it on every new machine
  (VM, Raspberry Pi) instead of hand-editing `~/.bashrc`.
- `install-deps.sh` — `rosdep` install of every package dependency in
  `src/`; run once after cloning and again when a package adds a dependency.

On a fresh machine: clone, `source scripts/env.sh`,
`./scripts/install-deps.sh`, `./scripts/build.sh`, `source scripts/env.sh`.
