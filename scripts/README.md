# scripts/

- `env.sh` - `source scripts/env.sh` sets up ROS 2 Jazzy, `ROS_DOMAIN_ID`
  (default 10), `ROBOT_NAMESPACE` (default `/robot_10`), Cyclone DDS like
  on the robot, and this workspace if it is built. Use it on every machine
  (VM, Raspberry Pi) instead of editing `~/.bashrc`.
- `install-deps.sh` - installs what the packages in `src/` need, with
  `rosdep`. Run it once after cloning and again when a package gets a new
  dependency.
- `build.sh` - `colcon build` of the workspace.
- `lint.sh` - `ruff` and `black --check`. Run it before every push, there
  is no CI.

On a fresh machine:

```bash
source scripts/env.sh
./scripts/install-deps.sh
./scripts/build.sh
source scripts/env.sh
```
