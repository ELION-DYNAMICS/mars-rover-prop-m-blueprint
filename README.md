# Mars Rover PROP-M Blueprint

Simulation-first Mars rover architecture inspired by the Soviet PrOP-M concept and rebuilt as a modern ROS 2 research stack.

This repository currently contains an integrated prototype stack with:
- Mechanical model (URDF/Xacro)
- Kinematics and dynamics documentation
- Control architecture (ros2_control)
- State estimation bringup
- Navigation configuration (Nav2)
- Deterministic mission-cycle execution aligned to BT-authored mission trees
- Multi-scenario simulation assets
- Logging + dataset governance
- Repository CI and regression workflow definitions

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

ROS 2 workspace (`ros_ws/`):

- `rover_description` -> Robot model, inertials, transmissions
- `rover_control` -> Wheel controllers, ros2_control configs
- `rover_estimation` -> Odometry + state fusion
- `rover_navigation` -> Nav2 configuration
- `rover_mission_bt` -> Mission-cycle runner and authored mission trees
- `rover_sim_gazebo` -> Simulation environments
- `rover_tools` -> Dataset export + metrics

---

## Current Maturity

This is an early engineering repository, not a finished flight or field stack.

- The simulation/control/navigation path is the strongest implemented surface.
- Mission execution currently uses a deterministic scheduler aligned to the BT phase model; it is not yet a full runtime tree executor.
- Dynamics and terramechanics parameters still include first-pass estimates pending calibration.
- Reproducibility depends on a ROS 2 / Gazebo environment with the declared package set available.

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

Scenario assets and regression workflow definitions are included in the repository. Their value depends on the local or CI environment being able to build and run the ROS 2 stack.

---

## Reproducibility

The intended run artifact set is:

- MCAP log
- run_metadata.json
- metrics.json

Packaged runs are schema-validated.
Regression thresholds are enforced when the corresponding evaluation pipeline is executed successfully.

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

_This repository is a technical reconstruction and modernization of early planetary surface mobility concepts, implemented as a ROS 2 research prototype with explicit room for calibration and integration hardening._
