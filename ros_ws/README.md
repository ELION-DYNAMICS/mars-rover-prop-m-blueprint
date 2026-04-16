# ROS Workspace (ros_ws)

This workspace contains the flight software stack for the Mars Rover Prop-M Blueprint program.

The intent is not to “run a rover in sim.”  
The intent is to build a rover software system that is testable, calibratable, traceable, and eventually portable from simulation to hardware without rewriting core logic.

---

## 1. Architecture Overview

At a high level, the system is organized as:

**Perception/Drivers** -> **State Estimation** -> **Navigation & Autonomy** -> **Command Shaping (Safety)** -> **Actuation** -> **Logging/Datasets**

Key boundary contracts:

- **Navigation publishes**: `/cmd_vel`
- **Control shapes**: `/cmd_vel` -> `/cmd_vel_safe` (limits, ramping, watchdog, slip containment)
- **Driver layer consumes**: `/cmd_vel_safe` and interfaces to sim/hardware actuators
- **Dataset tooling records** topics and packages immutable runs under `/datasets/`

This separation is intentional. It prevents the common failure mode where tuning, mission logic, drivers, and data collection become entangled and irreproducible.

---

## 2. Packages

### Core
- `rover_description`  
  URDF/Xacro, inertials, transmissions, mesh layout. Source of truth for frames and kinematic structure.

- `rover_control`  
  Command shaping and safety arbitration: watchdog timeout, velocity/accel limits, optional slip-based command degradation. Publishes `/cmd_vel_safe`.

- `rover_navigation`  
  Nav2 configuration profiles, costmaps, planner/controller plugin wiring. Navigation policy only (no physics enforcement).

- `rover_mission_bt`  
  Mission-cycle Behavior Trees: **Drive → Stop/Measure → Transmit/Log → Repeat**, with mode-specific behavior.

- `rover_msgs`  
  Custom message definitions (tactile bars, soil probe, run metadata).

### Simulation
- `rover_sim_gazebo`  
  Gazebo worlds, terrain presets, sensor configuration, world plugins. Simulation is treated as an experiment harness, not a demo.

### Drivers
- `rover_drivers` (umbrella package)
- `rover_driver_base`  
  Driver-layer boundary package. Simulation bridge nodes currently satisfy IMU, encoder, contact, and motor-interface contracts; hardware drivers are expected to replace those bridges later without changing higher layers.

### Operations / Evidence
- `rover_tools`  
  Bag recording/export, dataset packaging, schema validation, and metrics evaluation scaffolding. This is how runs become evidence.

---

## 3. Modes: Modern vs PROP-M

The stack supports two operational modes:

- **Modern mode**: higher speed targets, continuous navigation, richer sensor expectations.
- **PROP-M mode**: conservative “stop-measure-continue” behavior with low speed and strict command shaping.

Mode selection must be explicit in launch and configuration.  
If you can’t state what mode you ran, you did not run a valid experiment.

---

## 4. Frames, Units, Time

### Frames (baseline)
- `map`
- `odom`
- `base_link`

### Units
- SI only. No exceptions.

### Time
- Simulation uses `/clock` (`use_sim_time: true`)
- Hardware uses system/ROS time (`use_sim_time: false`)

Any node that silently mixes time sources is unacceptable in calibration work.

---

## 5. Build

From `ros_ws/`:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash

If you are running Gazebo, ensure the appropriate Gazebo ROS packages are installed for your environment.

⸻

6. Run (Typical Simulation Bringup)

A minimal bringup sequence is:
	1.	Launch simulation world and spawn rover
	2.	Start drivers (sim stubs or sim bridges)
	3.	Start control shaping (rover_control)
	4.	Start estimation (when available)
	5.	Start navigation (Nav2)
	6.	Start mission cycle (BT)

This workspace is structured so the above becomes a single bringup launch once all node implementations are present.

⸻

7. Datasets and Reproducibility

A run is only useful if it is reproducible.

Rules:
	•	Datasets are immutable once packaged under /datasets/<run_id>/
	•	Each dataset must include run_metadata.json that validates against datasets/schemas/run_metadata.schema.json
	•	Any derived artifacts (plots, calibration fits, reports) belong under analysis/ or calibration outputs—not inside raw datasets

When in doubt: treat logs as evidence. Evidence cannot be edited.

⸻

8. Engineering Standards (Non-Negotiable)
	•	Determinism: If a run cannot be repeated with the same commit/config/seed, it is not acceptable for calibration or regression.
	•	Traceability: Every parameter set and output must cite its dataset(s).
	•	Separation of concerns: navigation is not control, mission logic is not tuning, drivers are not estimators.
	•	Fail loudly: missing topics, invalid metadata, stale commands—these should stop or degrade safely, not “keep going.”

Confidence comes from reproducibility, not visual plausibility.

⸻

9. Where to Start

If you are new to the repository:
	1.	Confirm the URDF publishes correct frames (rover_description)
	2.	Confirm command shaping works (rover_control: /cmd_vel → /cmd_vel_safe)
	3.	Record a minimal bag and package it (rover_tools)
	4.	Only then add sensor realism, terrain complexity, and autonomy sophistication

Skipping steps produces impressive videos and useless engineering.

⸻

10. Roadmap (Near Term)
	•	Wire Gazebo sensor plugins in rover_description/urdf/rover_gazebo.xacro (IMU, lidar) to feed Nav2 and estimation
	•	Implement rover_estimation (EKF publishing /odometry/filtered + TF)
	•	Implement real metrics evaluation over MCAP (slip, dwell times, phase durations)
	•	Enable CI regression: fixed worlds + deterministic runs + acceptance checks
