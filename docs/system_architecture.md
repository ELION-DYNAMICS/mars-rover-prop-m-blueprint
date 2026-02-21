# System Architecture

This document defines the complete system-level architecture of the
Mars Rover Prop-M Blueprint.

It formalizes:

- Node graph
- Topic graph
- Data flow
- Control hierarchy
- Simulation vs hardware mode differences

This document is the authoritative structural reference for the runtime system.

---

# 1. Architectural Overview

The rover software stack is layered:

Level 3 -> Mission Executive  
Level 2 -> Navigation  
Level 1 -> Estimation  
Level 0 -> Low-Level Control  
Level -1 -> Actuation & Sensors  

All interactions occur through defined ROS 2 interfaces.
No direct actuator access from autonomy is permitted.

---

# 2. Node Graph

The following nodes are mandatory in nominal operation.

## 2.1 Core Nodes

/rover_bringup  
Launch orchestration and parameter loading.

/rover_description  
URDF publishing and TF static frames.

/rover_control  
Command arbitration, safety constraints, torque limiting.

/rover_estimation  
Extended Kalman Filter (state estimation).

/rover_navigation  
Nav2 stack (global + local planner).

/rover_mission  
Behavior Tree or structured mission state machine.

/rover_diagnostics  
Health monitoring and fault reporting.

---

## 2.2 Simulation-Specific Nodes

/rover_sim_bridge  
Physics engine interface (Gazebo/Webots).

/clock (simulation)

/ground_truth_publisher (evaluation only)

---

## 2.3 Hardware-Specific Nodes

/rover_driver_motor  
Motor controller interface.

/rover_driver_imu  
IMU hardware interface.

/rover_driver_encoder  
Wheel encoder interface.

/rover_driver_contacts  
Contact/tactile sensor interface.

---

# 3. Topic Graph

## 3.1 Command Path

/mission/goal  
    -> /rover_navigation  
        -> /cmd_vel  
            -> /rover_control  
                -> /cmd_vel_safe  
                    -> low-level controller  
                        -> actuators  

---

## 3.2 State Feedback Path

actuators  
    -> /joint_states  
    -> /imu/data  
    -> /wheel/slip_estimate  
        -> /rover_estimation  
            -> /odometry/filtered  
                -> /rover_navigation  
                -> /rover_mission  

---

## 3.3 Diagnostics and Events

All subsystems publish:

/diagnostics  
/mission/state  
/fault_state  

These are logged in all validation runs.

---

# 4. Data Flow

## 4.1 Nominal Autonomous Flow

1. Mission executive selects waypoint  
2. Navigation generates velocity command  
3. Control layer enforces safety  
4. Low-level controller computes torque  
5. Actuators move rover  
6. Sensors provide feedback  
7. Estimator updates state  
8. Navigation adjusts trajectory  

Closed-loop cycle continues.

---

## 4.2 PROP-M Mode Flow

Drive segment  
-> Stop  
-> Science measurement  
-> Log  
-> Resume  

Tether constraint evaluated continuously.

If boundary exceeded:

-> Command rejected  
-> Retreat behavior triggered  

---

# 5. Control Hierarchy

Control authority flows downward only.

Mission Executive  
    -> selects objectives  

Navigation  
    -> computes feasible path  

Control Layer  
    -> enforces constraints  
    -> limits velocity  
    -> slip containment  

Low-Level Control  
    -> wheel velocity tracking  
    -> torque control  

Actuators  
    -> mechanical motion  

Safety overrides supersede all higher layers.

---

# 6. Safety and Constraint Enforcement

Constraints enforced in control layer:

- Tether radius limit
- Maximum linear velocity
- Maximum angular velocity
- Maximum acceleration
- Slip ratio threshold
- Torque saturation

If conflict occurs:

Safety decision prevails.

---

# 7. Simulation Mode

Simulation mode includes:

- Physics engine integration
- Simulated sensors
- Deterministic clock
- Ground truth publishing (evaluation only)

Characteristics:

- use_sim_time = true
- Controlled noise injection
- Fixed random seed (for regression)

No direct simulation shortcuts allowed in autonomy.

---

# 8. Hardware Mode

Hardware mode includes:

- Real motor drivers
- Real sensor drivers
- Physical latency
- Encoder quantization
- Bias drift

Characteristics:

- Real-time clock
- Watchdog timers enabled
- Strict safety constraints
- Hardware fault monitoring

Autonomy stack remains unchanged.

Only driver layer differs.

---

# 9. Mode Switching

System mode defined at launch:

mode: simulation | hardware  

Mode determines:

- Driver nodes loaded
- Clock source
- Sensor configuration
- Parameter sets

Core architecture remains identical.

---

# 10. Determinism and Traceability

The architecture must ensure:

- Identical behavior for identical inputs
- No hidden parameter dependencies
- No implicit frame assumptions
- Version-controlled configuration

All node interactions must be observable via logged topics.

---

# 11. Architectural Principles

1. Clear separation of responsibility  
2. No autonomy-to-actuator shortcuts  
3. All safety in control layer  
4. All state from estimator  
5. All data logged in validation runs  
6. Simulation mirrors hardware interfaces  

---

# 12. Summary

The system architecture enforces:

- Layered autonomy
- Deterministic execution
- Safety-first control
- Mode isolation
- Traceable data flow

The rover behaves as a structured engineering system,
not a collection of interacting scripts.
