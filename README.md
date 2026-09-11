# Corrida - Robot Maze Navigation (Team 6)

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

* **Mark Rijpstra** - project lead: strategic decisions, organizational
  coordination, primary tutor/stakeholder contact.
* **Marjan Rahimof** - tactical planning: day-to-day task sequencing,
  shares communication duties with the lead.
* **Yehor Oblyvantsov** - repository & standards: repo/git workflow,
  `CONTRIBUTING.md`/`AGENTS.md`, IEEE report process, hardware and
  software technical support.
* **Daniel Chiemezie Nwadike** - research: problem-domain investigation,
  shares communication duties, standing physical access to the robot.
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
├── scripts/                 build/lint helpers
├── docs/
│   ├── REFERENCES.md         citation policy & bibliography (start here)
│   ├── git-cheatsheet.md     day-to-day git commands (clone/branch/pull/push/PR)
│   ├── course-materials/     archived course documents
│   ├── adr/                  architecture decision records
│   ├── learning-goals/       individual learning-goal + reflection pages
│   └── meeting-notes/        team meeting notes
├── IEEE/                    report draft (IEEE citation style, see IEEE/README.md)
└── vms/                     local-only; VM snapshots are git-ignored, see CONTRIBUTING.md
```

## Working rules

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full git workflow, commit
convention, code style, self-testing requirements, and definition of done;
[docs/git-cheatsheet.md](docs/git-cheatsheet.md) for the day-to-day
commands (clone, branch, pull, push, PR - including setting up a new
VM); and [docs/REFERENCES.md](docs/REFERENCES.md) for how every fact and
every piece of adapted code gets cited.