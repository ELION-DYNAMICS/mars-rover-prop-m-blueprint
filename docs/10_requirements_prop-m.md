# PROP-M Mode Requirements _(PrOP-M Reconstruction)_

_This document specifies testable requirements for “PROP-M mode”: a tether-limited, cyclic-drive rover mission profile inspired by PrOP-M.  
All requirements use SHALL language and include verification methods._

---

## 1) Scope and Assumptions

### 1.1 Scope
PROP-M mode covers:
- Tether-limited navigation near a lander
- Cyclic motion -> stop -> measure -> log
- Contact-based obstacle response
- Minimal sensing _(encoders, IMU, tactile/contact)_, with optional modern sensors disabled by default

### 1.2 Assumptions
- Rover operates on a 2D terrain surface _(heightmap allowed)_.
- Default kinematics: differential drive _(can be replaced; topic contracts remain)_.
- Lander pose is known in `map` frame at mission start.

---

## 2) Definitions

- **Lander frame:** reference position for tether constraint.
- **Tether radius R:** maximum permitted distance from lander origin.
- **Drive segment:** commanded traversal between science stops.
- **Science stop:** stationary period for measurement and logging.
- **Contact event:** tactile/bumper trigger indicating obstacle interaction.

---

## 3) Functional Requirements

### 3.1 Mission Lifecycle
**REQ-P-001** The system SHALL support a dedicated runtime configuration called `rover_prop_m_mode`.  
**Verify:** Launch test loads profile and publishes `/mission/state=PROP_M_ACTIVE`.

**REQ-P-002** The mission executive SHALL implement a cyclic loop:  
`Drive Segment -> Science Stop -> Log/Transmit -> Repeat` until stop condition.  
**Verify:** Behavior-tree/state-machine trace shows ordered transitions for N cycles.

**REQ-P-003** The system SHALL support start, pause, resume, and abort commands.  
**Verify:** Integration test issues commands and confirms state transitions within timeout.

---

### 3.2 Tether Constraint _(Primary Constraint)_
**REQ-P-010** The rover SHALL remain within tether radius R = 15.0 m of the lander origin during PROP-M mode.  
**Verify:** Scenario test `lander_tether_site` ensures `distance(rover, lander) <= 15.0 m` at all times.

**REQ-P-011** The system SHALL enforce tether constraint at the control/safety layer, independent of navigation stack behavior.  
**Verify:** Inject a goal outside radius; confirm rover motion is clamped/blocked and a constraint violation event is emitted.

**REQ-P-012** When a commanded goal would exceed the tether radius, the system SHALL:
1) reject or project the goal to the nearest feasible point on the tether boundary, and  
2) publish a mission event with reason code `TETHER_LIMIT`.  
**Verify:** Unit + integration tests confirm projection behavior and event emission.

**REQ-P-013** The system SHALL expose tether radius as a parameter `tether_radius_m` and SHALL default to 15.0 m in PROP-M mode.  
**Verify:** Parameter readback equals 15.0 on boot.

---

### 3.3 Drive Segment _(Cyclic Locomotion)_
**REQ-P-020** The rover SHALL execute drive segments of length `segment_length_m` _(default 1.5 m)_ in PROP-M mode.  
**Verify:** Scenario run logs segment completion distance within tolerance.

**REQ-P-021** The system SHALL provide maximum limits:
- `v_max_mps` _(default 0.05 m/s)_
- `a_max_mps2` _(default 0.10 m/s²)_
- `omega_max_rps` _(default 0.30 rad/s)_  
**Verify:** Command saturation test ensures limits are not exceeded.

**REQ-P-022** After each drive segment, the rover SHALL come to a complete stop before beginning measurement.  
**Verify:** `|cmd_vel|=0` and wheel velocities below threshold for `stop_settle_s` duration.

---

### 3.4 Science Stop _(Measurement Cycle)_
**REQ-P-030** Each science stop SHALL last `science_stop_duration_s` _(default 10 s)_ excluding settle time.  
**Verify:** Mission trace + timestamps confirm duration.

**REQ-P-031** The rover SHALL record at minimum:
- time
- rover pose estimate
- wheel encoder readings
- IMU sample(s)
- contact state  
**Verify:** Bag + exported dataset contains required fields.

**REQ-P-032** The rover SHALL publish a science event `SCIENCE_SAMPLE_TAKEN` per stop with unique sample ID.  
**Verify:** Event topic contains increasing IDs with no duplicates in a run.

---

### 3.5 Obstacle Handling _(Contact/Tactile Driven)_
**REQ-P-040** The rover SHALL subscribe to contact/tactile signals and SHALL treat any contact event as an obstacle encounter.  
**Verify:** Sim injects contact; mission enters recovery.

**REQ-P-041** On contact event during a drive segment, the rover SHALL execute recovery:
1) Stop immediately  
2) Reverse by `recovery_reverse_m` _(default 0.20 m)_
3) Rotate by `recovery_turn_rad` _(default 0.52 rad ≈ 30°)_  
4) Retry drive segment up to `recovery_retries` _(default 3)_  
**Verify:** Scenario `mars_rocks` triggers contact; trace shows steps with bounded retries.

**REQ-P-042** After `recovery_retries` failures, the rover SHALL transition to `MISSION_FAULT` and SHALL publish fault code `OBSTACLE_UNRECOVERABLE`.  
**Verify:** Forced-failure test produces fault transition and code.

---

### 3.6 Estimation and Frames
**REQ-P-050** The rover SHALL publish `tf` frames: `map`, `odom`, `base_link`, and wheel/joint frames.  
**Verify:** TF tree introspection test passes.

**REQ-P-051** The rover SHALL publish filtered odometry on `/odometry/filtered`.  
**Verify:** Topic exists; message rate within expected bounds.

---

### 3.7 Logging, Datasets, and Reproducibility
**REQ-P-060** Every PROP-M run SHALL produce:
- MCAP bag file
- `run_metadata.json`
- `metrics.json`  
**Verify:** CI regression run checks artifacts exist.

**REQ-P-061** `run_metadata.json` SHALL validate against `datasets/schemas/run_metadata.schema.json`.  
**Verify:** Schema validation step in pipeline must pass.

**REQ-P-062** The system SHALL log a mission event stream including:
- mode entry/exit
- segment start/complete
- science stop start/complete
- contact events
- tether violations / projections
- faults  
**Verify:** Event topic contains required categories.

---

## 4) Performance Requirements

**REQ-P-070** In SIM mode, scenario execution SHALL be deterministic given a fixed random seed.  
**Verify:** Two runs with same seed produce identical key metrics within tolerance.

**REQ-P-071** The rover SHALL achieve at least N=5 completed drive+science cycles in `mars_flat` within 10 minutes simulated time without faults.  
**Verify:** Regression test asserts cycle count and no faults.

---

## 5) Safety Requirements _(HW-oriented, enforced in both modes)_

**REQ-P-080** The safety layer SHALL implement a command watchdog: if `/cmd_vel` input is stale for `cmd_timeout_s` _(default 0.5 s)_, output SHALL be zero velocity.  
**Verify:** Stale-input test results in zeroed `/cmd_vel_safe`.

**REQ-P-081** The safety layer SHALL enforce absolute speed limits regardless of command source _(teleop, nav, mission script)_.
**Verify:** Command injection test is clamped.

---

## 6) Verification Matrix _(Summary)_

| Requirement Group | Method | Artifact |
|---|---|---|
| Tether constraint | Scenario regression | metrics.json + event log |
| Cyclic mission | Integration test | mission trace |
| Obstacle recovery | Scenario regression | event log + state transitions |
| Logging/datasets | CI artifact check | bag + metadata + metrics |
| Safety watchdog | Unit/integration | cmd_vel_safe behavior |

---

## 7) Default Parameters _(PROP-M Mode)_

- `tether_radius_m`: 15.0
- `segment_length_m`: 1.5
- `science_stop_duration_s`: 10.0
- `stop_settle_s`: 1.0
- `v_max_mps`: 0.05
- `a_max_mps2`: 0.10
- `omega_max_rps`: 0.30
- `recovery_reverse_m`: 0.20
- `recovery_turn_rad`: 0.52
- `recovery_retries`: 3
- `cmd_timeout_s`: 0.5

