# scripts/

Team-wide setup/build/lint helpers.

- `build.sh` — `colcon build` the workspace (requires ROS2 already sourced).
- `lint.sh` — run `ruff` + `black --check` before every push. The repo is
  private, so there's no CI to catch violations for you.
