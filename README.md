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

```bash
git clone https://github.com/yeoblyv/corrida.git
cd corrida
source /opt/ros/jazzy/setup.bash
./scripts/build.sh
source install/setup.bash
```

Package-specific run instructions live with each package under `src/` once
they exist.

## Hardware & environment

* **Robot:** iRobot Create 3 - 7x IR obstacle sensors, 4x cliff sensors,
  optical odometer.
* **Added:** self-installed LiDAR + Raspberry Pi.
* **Maze:** unknown to the robot, flat ground, walls at ~90°, may contain
  loops, fixed start/finish positions.
* **Run window:** 8 + 8 minutes (disjoint attempts) on demo day.
* **Environment:** ROS 2 Jazzy Jalisco on Ubuntu 24.04 (VM or Raspberry Pi
  4), Foxglove for visualization - see [AGENTS.md](AGENTS.md) for the full
  workshop environment and the AI assistant's operating rules.

Hardware and maze constraints per E. Bergsma, F. N. Martins, & F. J.
Guzman (personal communication, September 11, 2026, slides 6-8) - full
citation policy in [docs/REFERENCES.md](docs/REFERENCES.md).

## Team - Group 6

* **Mark Rijpstra** - leader: overall direction for the team.
* **Marjan Rahimof** - planning & communication: day-to-day task
  sequencing, main point of contact.
* **Yehor Oblyvantsov** - GitHub: repository, git workflow,
  `CONTRIBUTING.md`/`AGENTS.md`, compiles the final report.
* **Daniel Chiemezie Nwadike** - meeting minutes: keeps the record of
  what's decided at each meeting.
* Tutor: Ewout Bergsma.

Roles are primary accountability, not a coding hierarchy - everyone
contributes to the software roughly equally; see
[ADR-0001](docs/adr/0001-team-roles-and-working-agreement.md).

Roster and tutor assignment per E. Bergsma, F. N. Martins, & F. J.
Guzman (personal communication, September 11, 2026, slides 4-5).

## Deadlines

| Date | Deliverable | Graded |
| --- | --- | --- |
| 2026-09-20 | Individual learning goals + plan | No |
| 2026-09-29 | Group progress presentation | No |
| 2026-10-20 | Group demonstration | Yes |
| 2026-10-25 | Group report (IEEE, ≤6 pages) | Yes |
| 2026-11-02 | Individual reflection | No |

Per E. Bergsma, F. N. Martins, & F. J. Guzman (personal communication,
September 11, 2026, slide 3). If Brightspace ever states a different
date, Brightspace wins - update this table, the citation, and
[docs/course-materials/](docs/course-materials/) together.

## Repository structure

```
corrida/
├── src/                    ROS2 packages (colcon workspace) - see src/README.md
├── tests/                   pytest unit tests for hardware-independent logic
├── notebooks/                demos, exploration, cheatsheets - see notebooks/README.md
├── scripts/                  build/lint helpers
├── docs/
│   ├── REFERENCES.md         citation policy & bibliography (start here)
│   ├── git-cheatsheet.md     day-to-day git commands (clone/branch/pull/push/PR)
│   ├── assets/                images used in docs (e.g. the logo)
│   ├── course-materials/     archived course documents
│   ├── adr/                  architecture decision records
│   └── learning-goals/       individual learning-goal + reflection pages
├── IEEE/                    report draft (IEEE citation style, see IEEE/README.md)
├── vms/                     local-only; VM snapshots are git-ignored, see CONTRIBUTING.md
├── LICENSE                  MIT - code
└── LICENSE-DOCS             CC BY 4.0 - report & documentation
```

## Working rules

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full git workflow, commit
convention, code style, self-testing requirements, and definition of done;
[docs/git-cheatsheet.md](docs/git-cheatsheet.md) for the day-to-day
commands (clone, branch, pull, push, PR - including setting up a new
VM); and [docs/REFERENCES.md](docs/REFERENCES.md) for how every fact and
every piece of adapted code gets cited.

## License

Source code (`src/`, `scripts/`, `notebooks/`, `tests/`) is **MIT** -
see [LICENSE](LICENSE). The report and documentation (`IEEE/`, `docs/`)
are **CC BY 4.0** - see [LICENSE-DOCS](LICENSE-DOCS), which also states
the one thing a license can't grant: permission to use this work to
satisfy your own coursework on this or an equivalent assignment. That's
governed by Hanze's academic integrity policy, not by us. Rationale in
[ADR-0002](docs/adr/0002-licensing.md).