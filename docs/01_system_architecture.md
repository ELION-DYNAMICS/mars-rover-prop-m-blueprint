# System Architecture

This document defines the runtime architecture for:
- Node graph
- Topic graph
- Data flow
- Control hierarchy
- Simulation and hardware differences

---

## 1) Node Graph _(ROS 2)_

### Core Nodes
- `/rover_bringup` _(launch + parameter wiring)_
- `/rover_description` _(URDF/xacro, TF tree)_
- `/rover_drivers/*` _(driver-layer packages and sim bridges)_
- `/rover_control` _(controllers, cmd mux, safety)_
- `/rover_estimation` _(EKF / robot_localization)_
- `/rover_navigation` _(Nav2 stack + costmaps)_
- `/rover_mission_bt` _(mission behavior tree / state machine)_
- `/rover_sim_gazebo` _(Gazebo bridge, world control) [SIM ONLY]_
- `/rover_tools/*` _(bagging, dataset export, metrics)_

### Optional / Advanced
- `/rover_terramechanics` _(slip + sinkage estimator)_
- `/rover_fault_manager` _(health monitoring, degraded modes)_
- `/rover_perception` _(stereo/LiDAR pipeline)_ [Modern mode]

---

## 2) Topic Graph _(Interfaces)_

### Command Topics
- `/cmd_vel` _(geometry_msgs/Twist)_ [Nav2 -> Control]
- `/cmd_vel_safe` _(Twist)_ [Control -> low-level controller]
- `/mission/goal` _(custom)_ [Operator/Script -> Mission]
- `/mission/state` _(custom)_ [Mission -> Operator/UI]

### State / Feedback
- `/joint_states` _(sensor_msgs/JointState)_
- `/wheel/odometry_raw` _(nav_msgs/Odometry)_
- `/odometry/filtered` _(nav_msgs/Odometry)_ [EKF output]
- `/tf`, `/tf_static`

### Sensors
- `/imu/data` _(sensor_msgs/Imu)_
- `/contacts/*` _(custom or geometry_msgs/WrenchStamped)_
- `/camera/*` _(sensor_msgs/Image)_ [optional]
- `/lidar/points` _(sensor_msgs/PointCloud2)_ [optional]

### Navigation _(Nav2)_
- `/map` _(nav_msgs/OccupancyGrid)_
- `/scan` _(sensor_msgs/LaserScan)_ [if used]
- `/goal_pose` _(geometry_msgs/PoseStamped)_
- `/plan` _(nav_msgs/Path)_
- `/local_costmap/*`, `/global_costmap/*`

### Logging / Evaluation
- `/rosout`
- `/diagnostics` _(diagnostic_msgs/DiagnosticArray)_
- `/metrics/*` _(custom)_
- `/dataset/events` _(custom)_

---

## 3) Data Flow _(End-to-End)_

### A) Teleop / Operator Command Flow
Operator -> `/cmd_vel` -> `rover_control` -> `/cmd_vel_safe` -> controller -> actuators/sim -> feedback -> EKF -> Nav2/missions

### B) Autonomous Navigation Flow
Nav2 planner -> `/cmd_vel` -> `rover_control` -> actuators/sim -> sensors -> EKF -> Nav2 feedback loops

### C) Mission Loop _(PROP-M mode)_
Mission BT -> _(set waypoint within tether radius)_ -> Nav2 -> drive segment -> stop -> science action -> log -> repeat

### D) Dataset + Metrics Flow
All topics -> rosbag _(MCAP)_ -> `export_bag.py` -> `datasets/` -> `evaluate_metrics.py` -> reports

---

## 4) Control Hierarchy _(Who Commands Whom)_

### Level 3: Mission Executive
- Mission scheduler / authored BT phase model decides *what to do next*
- Issues high-level goals and mode switches

### Level 2: Navigation
- Nav2 decides *how to reach a goal*
- Produces velocity commands

### Level 1: Rover Control / Safety
- Enforces constraints:
  - tether radius
  - max speed/accel
  - slip limits / current limits
  - obstacle contacts -> recovery
- Arbitrates command sources _(teleop or nav or scripted)_

### Level 0: Low-Level Control
- Motor controllers / joint controllers
- Tracks wheel velocities/torques
- Publishes encoder feedback

---

## 5) Simulation and Hardware Mode Differences

### Common _(Identical in SIM and HW)_
- Mission layer _(BT)_
- Navigation _(Nav2)_
- Estimation _(EKF)_
- Control hierarchy + safety rules
- Topic contracts _(same message types)_

### SIM Mode
- Actuation via Gazebo/physics plugin bridge
- Sensors are simulated _(IMU, contacts, encoders, optionally camera/LiDAR)_
- Ground truth available _(for evaluation only)_
- Deterministic scenarios + seeded noise

**SIM-specific Nodes**
- `rover_sim_gazebo`
- `gz_ros2_bridge` _(or equivalent)_

### Hardware Mode
- Actuation via motor driver interfaces
- Real sensors with calibration
- Timing jitter + comms latency must be tolerated
- Safety is stricter _(E-stop, watchdog)_

**HW-specific Nodes**
- future hardware-driver packages replacing the current driver-base simulation bridges
- timing, health, and safety interfaces validated against the target platform

---

## 6) Modes _(Runtime Config)_

### Mode Switch: `rover_v1` or `rover_prop_m_mode`
- parameters define:
  - tether radius constraint ON/OFF
  - sensor set _(minimal or modern)_
  - mission behavior _(cyclic science or goal-based)_
  - nav2 profile selection _(configs/nav2_profiles/*)_

---

## 7) Contracts _(Non-Negotiable)_

- `/cmd_vel` is never sent directly to actuators _(must pass through safety)_
- every run generates:
  - MCAP bag
  - run metadata JSON
  - metrics report
- all topics used in metrics are versioned _(schema pinned)_
