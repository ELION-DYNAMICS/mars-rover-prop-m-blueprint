# Mars Rover PROP-M Blueprint

Simulation-first Mars rover research stack inspired by the Soviet PrOP-M concept and rebuilt around a modern ROS 2 workspace.

This repository currently contains:
- Robot description assets (URDF/Xacro)
- Control and ros2_control configuration
- State-estimation bringup
- Navigation configuration for a modern mode
- Deterministic mission-cycle execution aligned to authored BT phases
- Gazebo simulation assets
- Dataset and metrics tooling
- Core CI for the non-Gazebo workspace

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

## Verified Today

The strongest current evidence in this repository is:

- the core ROS 2 workspace builds in CI on Humble
- the control, estimation, navigation, mission, and tooling packages integrate as one buildable stack
- simulation launch assets and scenarios exist in-tree for heavier local or dedicated simulation use
- dataset and metrics conventions are defined and versioned in the repo

This is meaningful, but it is not the same thing as a validated hardware rover or a fully proven simulation program.

---

## Current Maturity

This is an early engineering repository, not a finished flight or field stack.

- The control/estimation/navigation path is the strongest implemented surface.
- Generic CI validates the core workspace on ROS 2 Humble without the Gazebo package set.
- Simulation bringup is present, but it is a heavier optional path and not the surface validated by generic CI.
- Mission execution currently uses a deterministic scheduler aligned to the BT phase model; it is not yet a full runtime tree executor.
- The hardware bringup path is an explicit placeholder until a validated driver stack exists.
- Dynamics, inertials, and terramechanics parameters still include first-pass estimates pending calibration.
- Reproducibility depends on a ROS 2 / Gazebo environment with the declared package set available.

## What CI Proves

The `build-and-test (humble)` workflow is intended to prove one narrow thing well:

- the core ROS 2 workspace installs dependencies, builds, and reaches test-result reporting cleanly on Ubuntu 22.04 / ROS 2 Humble

It does not prove:

- Gazebo simulation fidelity
- hardware-driver readiness
- calibrated rover dynamics
- a full end-to-end mission autonomy runtime

That boundary is intentional. The repository is stronger when CI claims less and proves it consistently.

## Quickstart (Simulation)

### 1. Build container
```bash
docker compose build
```


### 2. Launch flat Mars scenario
```bash
docker compose up sim
```


### 3. Send velocity command
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist ...
```


### 4. Record dataset
```bash
ros2 bag record -s mcap --all
```


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
