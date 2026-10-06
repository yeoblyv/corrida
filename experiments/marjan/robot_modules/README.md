# robot_modules

Behaviours for the iRobot Create 3 (robot 10), Group 6 — Introduction Project, Hanze SSE.
One shared base class + one module per behaviour + one `main.py` to choose which behaviour runs.
Uses only the **IR sensors** and the **bumper** (no LiDAR yet).

Author: Marjan Rahimof · Branch: `Marjan` · Folder: `experiments/marjan/robot_modules/`

---

## Quick start

```bash
cd ~/corrida_gh_marjan/corrida/experiments/marjan/robot_modules
python3 main.py wall_left     # left-hand wall follower (default)
python3 main.py wall_right    # right-hand wall follower
python3 main.py bump          # turn to face an obstacle and touch it with the front bumper
python3 main.py avoid         # simple reactive obstacle avoider
```

Stop with **Ctrl+C**: the wheels stop and the light ring goes back to normal.

> Only one person drives the robot at a time. Tell your group before you start.

---

## Files

```
robot_modules/
├── robot_base.py        ← everything that is the SAME for all behaviours
├── wall_follower.py     ← wall following (left or right)
├── bump_target.py       ← aim at an obstacle and touch it with the front bumper
├── obstacle_avoider.py  ← simple reactive avoider (no memory)
├── main.py              ← chooses which behaviour to run
└── README.md            ← this file
```

| File | What is inside | Change it when… |
|---|---|---|
| `robot_base.py` | class `RobotBase`: IR + bumper listening, light ring, `change_state`, `time_in_state`, `drive`, `stop`, the 10 Hz timer | something changes for **all** behaviours (e.g. robot name, a new sensor) |
| `wall_follower.py` | class `WallFollower(side)` + its settings | tuning or improving wall following |
| `bump_target.py` | class `BumpTarget` + its settings | tuning or improving the bump behaviour |
| `obstacle_avoider.py` | class `ObstacleAvoider` + its settings | tuning the simple avoider |
| `main.py` | the `BEHAVIOURS` list and start/stop code | adding a new behaviour |

---

## Concepts

### Module
A module is just a `.py` file. Files in the same folder can use each other's code with `import`:

```python
from wall_follower import WallFollower   # open wall_follower.py, take WallFollower from it
```

### Inheritance: write shared code once
```
Node                (from ROS 2)
 └── RobotBase      (robot_base.py: IR, bumper, lights, states, timer, drive)
      ├── WallFollower      (wall_follower.py)
      ├── BumpTarget        (bump_target.py)
      └── ObstacleAvoider   (obstacle_avoider.py)
```
`class WallFollower(RobotBase)` means: *WallFollower gets everything RobotBase can do, and adds its own decisions.*

### How one cycle works (10 times per second)
```
RobotBase.control_loop()
    │
    ├── 1. SENSE   newest IR values are already stored in self.ir (by ir_callback)
    ├── 2. THINK   linear, angular = self.decide()      ← written by each behaviour
    └── 3. ACT     self.drive(linear, angular)          → /robot_10/cmd_vel
                   + one log line
```
A behaviour only has to answer one question in `decide()`:
**"In my current state, what do I do now?"** and return `(linear, angular)`.

### Units and signs
| Value | Unit | Sign |
|---|---|---|
| `linear` | m/s | + forward, − backward |
| `angular` | rad/s | **+ turn left**, − turn right |
| IR values | no unit | **bigger = closer** |

### Tools available in every behaviour (from `RobotBase`)
| Method | Returns |
|---|---|
| `self.front()` | max of the two front-centre IR sensors (wall straight ahead) |
| `self.front_wide()` | max of all four front IR sensors |
| `self.left()` | max of `side_left` and `left` |
| `self.right()` | max of `right` and `front_right` |
| `self.ir_value(name)` | one sensor, e.g. `'front_left'` |
| `self.take_bump()` | bumper part hit since last call (e.g. `'bump_front_center'`) or `None` |
| `self.change_state(s)` | switch state, restart the timer, set the light colour |
| `self.time_in_state()` | seconds since the current state started |
| `self.debug = '...'` | extra text shown in the log line |

---

## Behaviours

### 1. Wall follower — `wall_left` / `wall_right`
Keep a wall on one side (left-hand or right-hand rule). One module, mirrored by the `side` setting.

| State | Robot does | Light |
|---|---|---|
| `FIND_WALL` | drive straight until a wall is found | white |
| `FOLLOW_WALL` | drive along the wall with P-control; in narrow passages centre between walls (`(narrow)` in log) | green |
| `TURN_AWAY` | inside corner: rotate away from the wall (left side → turn right) until front is clear | blue |
| `TURN_INTO` | opening on the wall side: drive 0.8 s, then curve into it | yellow |
| `BACK_UP` | bumper hit: reverse, rotate away, follow again | red |

Techniques: state machine (memory), hysteresis (`FRONT_BLOCKED` 300 / `FRONT_CLEAR` 150), proportional steering (`error = near − target`), centring (`error = near − far`).

**Demo tip:** if the left-hand rule loops in round 1, run `wall_right` in round 2.

### 2. Bump target — `bump`
Wait until an obstacle appears, turn to face it, touch it with the front of the bumper.

| State | Robot does | Light |
|---|---|---|
| `WAIT` | stand still (or look around if `SCAN_TURN` > 0) | white |
| `AIM` | rotate until the front-centre sensors see the obstacle most | yellow |
| `APPROACH` | drive slowly straight at it | orange |
| `HIT` | bumper touched: stand still 1 s; log shows which bumper part | red |
| `RETREAT` | reverse a few cm, then wait again | magenta |

Direction of the obstacle = weighted average of sensor directions:
`direction = Σ(value × sensor_direction) / Σ value` (+ = left, − = right, ≈0 = ahead).
After a hit, the obstacle must be removed (IR < `LOST`) before the robot reacts again.
Test it in open space — in the maze, walls count as obstacles too.

### 3. Obstacle avoider — `avoid`
Reactive, no memory. Priority rules, first match wins:
1. wall ahead → turn towards the more open side
2. too close left → steer right
3. too close right → steer left
4. otherwise → straight

---

## Settings to calibrate

All settings are at the top of each behaviour file (CAPITAL names).

| File | Setting | Start | How to measure | Measured |
|---|---|---|---|---|
| wall_follower | `WALL['left']['target']` | 200 | left side ~5 cm from a wall, read `left=` | |
| wall_follower | `WALL['left']['lost']` | 40 | no wall nearby, read `left=`, set a bit above | |
| wall_follower | `WALL['right']['close']` | 150 | robot centred in narrow passage, read `right=`, set a bit below | |
| wall_follower | `WALL['right'][...]` | 200/40/150 | same, for the right side (only 1 sensor!) | |
| wall_follower | `FRONT_BLOCKED` / `FRONT_CLEAR` | 300 / 150 | turns too early/late at inside corners? | |
| wall_follower | `KP`, `KP_CENTER` | 0.002 | zig-zag → smaller; drifts away → bigger | |
| bump_target | `DETECT` | 60 | box 5–10 cm away should exceed it; nothing near should not | |
| bump_target | `MAX_AIM_TURN` | 0.6 | rotates past the obstacle → smaller | |

---

## Adding a new behaviour

1. Create `my_behaviour.py`:

```python
from robot_base import RobotBase

START = 'START'

class MyBehaviour(RobotBase):
    STATE_COLORS = {START: (0, 255, 0)}

    def __init__(self):
        super().__init__('my_behaviour', first_state=START)

    def decide(self):
        if self.front() > 300:
            return 0.0, 0.5        # turn left
        return 0.1, 0.0            # drive forward
```

2. Register it in `main.py`:

```python
from my_behaviour import MyBehaviour
BEHAVIOURS = { ..., 'mine': MyBehaviour }
```

3. Run: `python3 main.py mine`

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ros2: command not found` / no topics | `source /opt/ros/jazzy/setup.bash`, `export ROS_DOMAIN_ID=10`, `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` (put them in `~/.bashrc`) |
| `ModuleNotFoundError: No module named 'robot_base'` | run `main.py` from inside the `robot_modules` folder |
| No log lines at all | no IR data: check `ros2 topic echo /robot_10/ir_intensity` |
| Robot does not move in `bump` | it is waiting: bring the obstacle closer (5–10 cm), lower `DETECT`, or set `SCAN_TURN = 0.3` |
| Robot does not react after a hit | remove the obstacle completely first (re-arming) |


