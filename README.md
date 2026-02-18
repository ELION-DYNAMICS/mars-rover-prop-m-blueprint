# Mars Rover PROP-M Blueprint

Simulation-first, research-grade Mars rover architecture inspired by the Soviet PrOP-M concept - rebuilt with modern robotics standards.

This repository contains a complete, reproducible rover stack:
- Mechanical model (URDF/Xacro)
- Kinematics and dynamics documentation
- Control architecture (ros2_control)
- State estimation
- Navigation stack (Nav2)
- Mission logic (Behavior Trees)
- Multi-scenario simulation
- Logging + dataset governance
- CI-backed regression testing

---

## Mission Philosophy

PROP-M was simple:
Drive -> Stop -> Measure -> Transmit -> Repeat.

This project preserves that deterministic philosophy while enabling modern autonomy extensions.

Two operational modes:

1. **PROP-M Mode**
   - Tether-limited radius (~15 m)
   - Cyclic movement logic
   - Contact-triggered obstacle avoidance
   - Deterministic mission cadence

2. **Modern Mode**
   - Full Nav2 navigation
   - SLAM-ready
   - Recovery behaviors
   - Modular autonomy stack

---

## System Architecture

ROS 2 workspace (`rover_ws/`):

- `rover_description` -> Robot model, inertials, transmissions
- `rover_control` -> Wheel controllers, ros2_control configs
- `rover_estimation` -> Odometry + state fusion
- `rover_navigation` -> Nav2 configuration
- `rover_mission_bt` -> Mission behavior trees
- `rover_sim_gazebo` -> Simulation environments
- `rover_tools` -> Dataset export + metrics

---

## Quickstart (Simulation)

### 1. Build container
docker compose build


### 2. Launch flat Mars scenario
docker compose up sim


### 3. Send velocity command
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist ...


### 4. Record dataset
ros2 bag record -s mcap --all


---

## Scenarios

| Scenario | Purpose |
|----------|----------|
| mars_flat | Kinematics + control validation |
| mars_rocks | Obstacle avoidance stress |
| mars_dunes | Slip + terrain interaction |
| lander_tether_site | PROP-M tether realism |

All scenarios are regression-tested.

---

## Reproducibility

Every simulation run produces:

- MCAP log
- run_metadata.json
- metrics.json

Runs are schema-validated.
CI fails if performance thresholds regress.

---

## Engineering Standards

- Simulation-first development
- No feature without metrics
- No autonomy without logging
- No merge without CI passing
- No undocumented parameter

---

## Licensing

Software: Apache 2.0  
Hardware designs: CERN-OHL  
Datasets: CC-BY 4.0  

See `/LICENSES` for details.

---

## Roadmap

v0.1 – Simulation MVP  
v0.2 – Navigation + scenario regression  
v0.3 – Full PROP-M mission loop  
v1.0 – Terramechanics + calibrated dynamics  

---

## Research Intent

_This repository is a technical reconstruction and modernization of early planetary surface mobility concepts, engineered under contemporary robotics standards._
