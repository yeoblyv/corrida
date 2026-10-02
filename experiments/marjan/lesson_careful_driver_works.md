# Lesson: how careful_driver.py works (Marjan, 2 Oct 2026)

First working obstacle-avoiding behaviour on robot 10 (runs on the Pi as user marjan, `python3 careful_driver.py`).

## Big idea: sense → think → act
Two independent rhythms run inside one program:
- LISTEN (`ir_callback`): runs every time the robot publishes IR data; only writes the newest 7 values into the dictionary `self.ir`.
- THINK + ACT (`control_loop`): runs 10×/s from a timer; reads `self.ir`, decides, publishes one Twist on `/robot_10/cmd_vel`.

## Decision rules (checked top to bottom, first match wins)
1. front > FRONT_THRESHOLD (300) → stop, rotate towards the more open side (left > right ⇒ turn right, else turn left).
2. left > SIDE_THRESHOLD (200) → drive forward, steer slightly right.
3. right > SIDE_THRESHOLD → drive forward, steer slightly left.
4. else → straight.
front = max of 4 front sensors, left = max(side_left, left), right = right (only one sensor on the right).
Positive angular.z = turn left (counter-clockwise), negative = turn right.

## Observations so far
- Robot stops ~415 even with threshold 300 → reaction delay/overshoot (10 Hz loop + braking).
- IR values fluctuate ±10 at a fixed distance → sensor noise.
- Front-only version scraped left walls (blind sides + always turning left) → fixed by using side sensors.

## Known limitations / next steps
No memory (purely reactive) → can loop forever in a maze with loops or dead ends; can jitter around thresholds (needs hysteresis / state machine); IR only sees ~tens of cm; no bumper fallback yet (`hazard_detection`); LiDAR not used yet (bonus +0.5).