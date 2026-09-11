# src/

ROS2 colcon workspace source folder — the repository root is the workspace
root. `colcon build` runs from there and produces `build/`, `install/`,
`log/`, all git-ignored (see `.gitignore`).

Each ROS2 package lives in its own subdirectory here, e.g.:

```
src/
├── corrida_bringup/       # launch files, robot/LiDAR bring-up
├── corrida_perception/    # IR + LiDAR fusion, obstacle/wall detection
└── corrida_navigation/    # maze-solving / wall-following logic
```

Conventions:

- Package names `snake_case`, prefixed `corrida_`.
- One responsibility per package.
- Keep pure algorithmic logic (no ROS2/rclpy dependency) in plain,
  importable Python so it can be unit-tested under `tests/` without a
  running robot or simulator — see `CONTRIBUTING.md` for the test and
  review rules that apply to everything added here.
