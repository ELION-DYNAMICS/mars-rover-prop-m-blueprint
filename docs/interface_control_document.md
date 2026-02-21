# Interface Control Document (ICD)

This document defines the formal interface contracts between all subsystems
in the Mars Rover Prop-M Blueprint.

It governs:

- Message definitions
- Topic contracts
- QoS policies
- Frame conventions
- Units policy
- Timestamp policy

No subsystem may deviate from this document without revision.

---

# 1. Message Contracts

All inter-node communication must use explicitly defined message types.

Standard ROS message types are preferred.

Custom messages must be defined in:

rover_msgs/

---

## 1.1 Command Interface

Topic:
`/cmd_vel`

Type:
geometry_msgs/Twist

Semantics:
- linear.x  -> forward velocity [m/s]
- angular.z -> yaw rate [rad/s]

All other fields must be zero.

---

## 1.2 Safe Command Interface

Topic:
`/cmd_vel_safe`

Type:
geometry_msgs/Twist

Source:
Control arbitration layer

Only `/cmd_vel_safe` may reach low-level control.

---

## 1.3 State Estimate

Topic:
`/odometry/filtered`

Type:
nav_msgs/Odometry

Must contain:
- pose
- twist
- covariance

Frame IDs must comply with Section 3.

---

## 1.4 Wheel Slip Estimate

Topic:
`/wheel/slip_estimate`

Type:
std_msgs/Float64 (per wheel) or custom Slip.msg

Units:
dimensionless ratio

---

## 1.5 Mission State

Topic:
`/mission/state`

Type:
custom MissionState.msg

Must include:
- current_state
- goal_id
- recovery_count
- tether_distance

---

# 2. Topic QoS Policy

QoS must be explicitly defined for every topic.

Default profile: RELIABLE unless otherwise specified.

---

## 2.1 High-Rate Sensor Topics

Examples:
- /imu/data
- /joint_states

QoS:
- Reliability: BEST_EFFORT
- History: KEEP_LAST
- Depth: 10

Rationale:
High-rate data tolerates minor loss.

---

## 2.2 State and Command Topics

Examples:
- /cmd_vel
- /cmd_vel_safe
- /odometry/filtered

QoS:
- Reliability: RELIABLE
- History: KEEP_LAST
- Depth: 10

Rationale:
Commands and state must not be silently dropped.

---

## 2.3 Mission and Control Events

Examples:
- /mission/state
- /diagnostics

QoS:
- Reliability: RELIABLE
- History: KEEP_LAST
- Depth: 5

---

# 3. Frame Conventions

All coordinate frames must follow REP-103 conventions.

Right-handed coordinate system:

- X forward
- Y left
- Z up

---

## 3.1 Required Frames

map
odom
base_link
wheel_left
wheel_right

---

## 3.2 Transform Tree

map
  -> odom
      -> base_link
          -> wheel_left
          -> wheel_right

Only the estimator may publish:

odom -> base_link

Only SLAM (if enabled) may publish:

map -> odom

No node may publish conflicting transforms.

---

# 4. Units Policy

All physical quantities must use SI units.

Position:
meters (m)

Velocity:
meters per second (m/s)

Angular velocity:
radians per second (rad/s)

Acceleration:
meters per second squared (m/s²)

Torque:
Newton-meters (Nm)

Mass:
kilograms (kg)

Force:
Newtons (N)

Angles:
radians (internal)
degrees permitted only for logging display

No mixed unit systems allowed.

---

# 5. Timestamp Policy

All messages must include valid ROS time stamps.

Simulation mode:

- use_sim_time = true
- Time derived from simulation clock

Hardware mode:

- Time derived from system clock synchronized via NTP

Timestamps must represent:

Measurement acquisition time,
not message publication time.

Latency-sensitive modules must account for:

Δt between measurement and processing.

---

# 6. Determinism Requirements

Message definitions must remain stable.

Any change to message structure requires:

- Version increment
- Documentation update
- Regression testing

No silent interface changes permitted.

---

# 7. Logging Requirements

All interface topics listed in this document
must be recorded in MCAP during validation runs.

If a topic is critical to control or estimation,
it must be logged.

---

# 8. Change Control

Any modification to:

- Message types
- Topic names
- QoS settings
- Frame structure
- Units
- Timestamp behavior

Requires:

- ICD revision update
- Review
- Regression verification

---

# 9. Summary

Interfaces are contracts.

Contracts must be:

- Explicit
- Stable
- Versioned
- Testable

No implicit assumptions allowed.

If two nodes disagree about:

units  
frames  
timestamps  

the system is considered invalid.
