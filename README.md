<p align="center">
  <img src="docs/assets/banner.svg" alt="Corrida: robot maze navigation, Team 6. An iRobot Create 3 with bull horns." width="100%">
</p>

<p align="center">
  <img alt="robot: iRobot Create 3" src="https://img.shields.io/badge/robot-iRobot%20Create%203-D9BD84?style=flat-square&labelColor=1F2326&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjQgMCAxMTIgOTYiPjxwYXRoIGZpbGw9IiNmZmYiIGZpbGwtcnVsZT0iZXZlbm9kZCIgZD0iTTQwIDI1TDQxIDVMMzMgMTNMMzAgMjRMMzYgMzZMNDMgNDVMNTEgNDRMNTEgNTBMNTMgNTNMNjEgNTRMNjggNTJMNjkgNTBMNjkgNDBMNjkgMzlMNjQgMzZMNTcgMzZMNTIgMzhMNTEgNDFMNDUgMzVaTTUxIDQ0TDU0IDQ2TDYwIDQ3TDY2IDQ2TDY5IDQzTDY5IDQ4TDY3IDUwTDY0IDUxTDU2IDUxTDUxIDQ4Wk05MyAxMEw5NSAzMkw4OSA0M0w4MCA1Mkw5MSA1NEw5OSA0NEwxMDUgMzFMMTAyIDE5Wk01NiAzNEw1MCAzNEw0OCAzNUw1MCAzN1pNODkgMzhMNzYgMzVMNjQgMzRMNjkgMzZMNzEgMzhMODcgNDFaTTE0IDczTDE2IDc4TDIxIDgzTDI5IDg3TDM4IDg5TDQ4IDkxTDU5IDkyTDcwIDkxTDgyIDkwTDk2IDg1TDEwMSA4MUwxMDQgNzhMMTA2IDcyTDEwNiA1MkwxMDQgNDhMMTAxIDQ1TDk5IDQ4TDEwMyA1M0wxMDMgNTZMMTAxIDU5TDk0IDY0TDgyIDY4TDYyIDcxTDQwIDY5TDMyIDY2TDI0IDYzTDE5IDU5TDE3IDU1TDE4IDUxTDIyIDQ3TDI4IDQzTDM2IDQwTDM0IDM3TDIzIDQyTDE4IDQ2TDE1IDQ5TDE0IDUzWk0zNSA4MkwyMSA3NEwyMSA2OUwzNSA3OFpNNDggODVMNDggODFMNjggNzhMNjggODNaIi8+PC9zdmc+">
  <img alt="LiDAR: RPLIDAR A1M8" src="https://img.shields.io/badge/LiDAR-RPLIDAR%20A1M8-D9BD84?style=flat-square&labelColor=1F2326">
  <img alt="compute: Raspberry Pi 4" src="https://img.shields.io/badge/compute-Raspberry%20Pi%204-D9BD84?style=flat-square&labelColor=1F2326&logo=raspberrypi&logoColor=white">
  <br>
  <a href="https://docs.ros.org/en/jazzy/"><img alt="ROS 2: Jazzy Jalisco" src="https://img.shields.io/badge/ROS%202-Jazzy%20Jalisco-C8102E?style=flat-square&labelColor=1F2326&logo=ros&logoColor=white"></a>
  <a href="https://releases.ubuntu.com/24.04/"><img alt="Ubuntu: 24.04 LTS" src="https://img.shields.io/badge/Ubuntu-24.04%20LTS-C8102E?style=flat-square&labelColor=1F2326&logo=ubuntu&logoColor=white"></a>
  <img alt="Python: 3.12" src="https://img.shields.io/badge/Python-3.12-C8102E?style=flat-square&labelColor=1F2326&logo=python&logoColor=white">
  <img alt="SLAM: slam_toolbox" src="https://img.shields.io/badge/SLAM-slam__toolbox-C8102E?style=flat-square&labelColor=1F2326">
  <br>
  <img alt="course: SEVM25IP" src="https://img.shields.io/badge/course-SEVM25IP-F5EFE4?style=flat-square&labelColor=1F2326">
  <img alt="demo: 2026-10-20" src="https://img.shields.io/badge/demo-2026--10--20-F5EFE4?style=flat-square&labelColor=1F2326">
  <img alt="status: active" src="https://img.shields.io/badge/status-active-F5EFE4?style=flat-square&labelColor=1F2326">
  <a href="LICENSE"><img alt="License: MIT (code) / CC BY 4.0 (docs)" src="https://img.shields.io/badge/license-MIT%20%2F%20CC%20BY%204.0-F5EFE4?style=flat-square&labelColor=1F2326"></a>
</p>

<p align="center">
  <a href="#about"><b>About</b></a> &nbsp;·&nbsp;
  <a href="#quickstart"><b>Quickstart</b></a> &nbsp;·&nbsp;
  <a href="#hardware--environment"><b>Hardware</b></a> &nbsp;·&nbsp;
  <a href="#team---group-6"><b>Team</b></a> &nbsp;·&nbsp;
  <a href="#deadlines"><b>Deadlines</b></a> &nbsp;·&nbsp;
  <a href="#repository-structure"><b>Structure</b></a> &nbsp;·&nbsp;
  <a href="#working-rules"><b>Working rules</b></a> &nbsp;·&nbsp;
  <a href="#license"><b>License</b></a>
</p>

## About

Hanze Master Smart Systems Engineering, Introduction Project -
Semester 1, 2026/2027. Program an iRobot Create 3 to autonomously navigate
an unknown maze, fusing its IR proximity sensors and a self-installed LiDAR, via ROS2.

## Quickstart

On Ubuntu 24.04 with ROS 2 Jazzy:

```bash
git clone https://github.com/yeoblyv/corrida.git
cd corrida
source scripts/env.sh
./scripts/install-deps.sh
./scripts/build.sh
source scripts/env.sh
```

On the robot's Pi, with the lidar plugged in, this starts the lidar driver
and slam_toolbox:

```bash
ros2 launch corrida_bringup bringup.launch.py
```

## Hardware & environment

* **Robot:** iRobot Create 3 - 7x IR obstacle sensors, 4x cliff sensors,
  optical odometer.
* **Added:** self-installed LiDAR (RPLIDAR A1M8) + Raspberry Pi 4.
* **Maze:** unknown to the robot, flat ground, walls at about 90 degrees,
  may contain loops, fixed start/finish positions.
* **Run window:** 8 + 8 minutes (disjoint attempts) on demo day.
* **Environment:** ROS 2 Jazzy Jalisco on Ubuntu 24.04 (VM or Raspberry Pi
  4), Foxglove for visualization. [AGENTS.md](AGENTS.md) has the rules for
  AI assistants used with this repo.

## Team - Group 6

* **Mark Rijpstra** - leader
* **Marjan Rahimof** - planning and communication
* **Yehor Oblyvantsov** - GitHub and the repo, puts the final report together
* **Daniel Chiemezie Nwadike** - meeting minutes
* Tutor: Ewout Bergsma

Everyone works on the code. The roles are from our first meeting, see
[ADR-0001](docs/adr/0001-team-roles-and-working-agreement.md).

## Deadlines

| Date | Deliverable | Graded |
| --- | --- | --- |
| 2026-09-20 | Individual learning goals + plan | No |
| 2026-09-29 | Group progress presentation | No |
| 2026-10-20 | Group demonstration | Yes |
| 2026-10-25 | Group report (IEEE, max 6 pages) | Yes |
| 2026-11-02 | Individual reflection | No |

The dates, the maze rules and the group list are from the kickoff slides
(E. Bergsma, F. N. Martins, & F. J. Guzman, personal communication,
September 11, 2026). If Brightspace says something else, Brightspace wins.

## Repository structure

- `src/` - ROS 2 packages (colcon workspace)
- `tests/` - pytest tests for logic that doesn't need the robot
- `notebooks/` - Jupyter notebooks with demos and notes
- `scripts/` - setup, build and lint helpers
- `docs/` - git cheatsheet, Pi accounts, references, decisions (`adr/`)
- `vms/` - local VM snapshots, not in git

## Working rules

How we work is in [CONTRIBUTING.md](CONTRIBUTING.md). The day-to-day git
commands are in [docs/git-cheatsheet.md](docs/git-cheatsheet.md), and how
we cite sources is in [docs/REFERENCES.md](docs/REFERENCES.md).

## License

Code (`src/`, `scripts/`, `notebooks/`, `tests/`) is MIT, see
[LICENSE](LICENSE). The documentation and the report are CC BY 4.0, see
[LICENSE-DOCS](LICENSE-DOCS). A license doesn't allow using this work for
your own coursework, Hanze's academic integrity rules decide that. Why
there are two licenses is in [ADR-0002](docs/adr/0002-licensing.md).
