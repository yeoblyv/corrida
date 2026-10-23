# Raspberry Pi: adding a team member's account

How to give a teammate their own account on the robot's Raspberry Pi, so
they can run code from their own branch in their own directory. Done by
hand, once per person, by whoever has `sudo` on the Pi.

Assumes Ubuntu 24.04 with ROS 2 Jazzy already installed system-wide (one
install serves every user). Commands marked **(admin)** run as the
administrator account; the rest run as the new user.

## 1. Create the account (admin)

```bash
sudo adduser <username>
```

Answer the prompts (password, full name). Use the person's first name,
lowercase, as `<username>`.

Give access to the robot's hardware (LiDAR serial port, camera). This is
the same set the `ros2` account uses on the desktop; do **not** add `sudo`
unless the person really needs to administer the Pi:

```bash
sudo usermod -aG sudo,dialout,plugdev,video <username>
```

Check the result:

```bash
id <username>
```

The new groups apply from the next login.

## 2. First-time setup as the new user

Log in as the new user, then install the GitHub CLI once per machine
(admin, since it is a system package):

```bash
sudo apt install -y gh
```

As the new user:

```bash
gh auth login
git config --global user.name "Your Full Name"
git config --global user.email "your.email@used.on.github"
```

The repository is private, so the GitHub account used here must be a
collaborator on `yeoblyv/corrida`. Every person signs in with their own
account; never share a token.

## 3. Clone your own branch

Branch names are listed in [git-cheatsheet.md](git-cheatsheet.md) (`mark`,
`Marjan`, `Daniel`, `yehor`):

```bash
git clone -b <your-branch> https://github.com/yeoblyv/corrida.git
cd corrida
source scripts/env.sh
./scripts/install-deps.sh
./scripts/build.sh
source scripts/env.sh
```

Each user gets their own `~/corrida` with their own `build/`, `install/`
and `log/`, so branches and builds never interfere. `install-deps.sh`
asks for `sudo` once (rosdep); a user without `sudo` asks the admin to run
it.

To run the stack:

```bash
ros2 launch corrida_bringup bringup.launch.py
```

## 4. Working rules

- Follow [CONTRIBUTING.md](../CONTRIBUTING.md): work on your own branch,
  Conventional Commits, `./scripts/lint.sh` before pushing.
- On the Pi, put the platform in the visible part of the commit title, e.g.
  `feat(navigation): add wall-following state machine [Ubuntu 24.04, robot]`.
- Push before you log out; an unpushed change lives only on the Pi.

## 5. One robot, many users: safety

All accounts share one robot, one `ROS_DOMAIN_ID` and one namespace
(`/robot_10`). Two people launching their stacks at the same time publish
to the same topics, and the robot receives conflicting motion commands. The
LiDAR's serial port can also be opened by only one process at a time.

- **One active session at a time** for anything that can move the robot or
  read the LiDAR; agree who has the robot before launching.
- Tests that do not move the robot can use a different domain, for example
  `export ROS_DOMAIN_ID=11` before `source scripts/env.sh`.
- Run the physical-safety checks from the workshop material before any
  motion command.

