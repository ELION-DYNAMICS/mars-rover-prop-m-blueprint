# Planning and Autonomy

This document defines the rover’s autonomy architecture, planning structure,
and execution logic.

The autonomy layer is responsible for:

- Goal interpretation
- Path planning
- Local obstacle avoidance
- Mission sequencing
- Constraint enforcement (PROP-M mode)
- Recovery behaviors

It operates through defined control interfaces only.

---

# 1. Autonomy Architecture Overview

Autonomy is structured in three layers:

Level 3 -> Mission Executive  
Level 2 -> Navigation Stack  
Level 1 -> Safety and Constraint Enforcement  

Command hierarchy:

Mission Executive  
    -> Goal request  
    -> Navigation  
    -> Velocity command  
    -> Low-level control  

Each layer must be independently testable.

---

# 2. Mission Executive

The mission executive defines what the rover is attempting to accomplish.

Implementation: Behavior Tree (BT) or structured state machine.

## 2.1 Responsibilities

- Accept high-level objectives
- Decompose into waypoint segments
- Enforce mission sequencing
- Trigger science actions
- Handle recoveries
- Enforce tether constraint (PROP-M mode)

## 2.2 Mission Cycle (PROP-M Mode)

Nominal cycle:

Drive segment  
-> Stop  
-> Stabilize  
-> Execute measurement  
-> Log result  
-> Select next segment  

Cycle repeats until:

- Radius limit reached
- Obstacle impassable
- Mission complete
- Fault condition triggered

---

# 3. Navigation Layer

Navigation computes *how* to reach a target pose.

Recommended architecture: Nav2 (ROS 2)

Components:

- Global Planner
- Local Planner (Controller)
- Costmaps (global + local)
- Recovery behaviors

---

## 3.1 Global Planning

Inputs:
- Current pose (EKF)
- Goal pose
- Global costmap

Outputs:
- Path (nav_msgs/Path)

Planner must:

- Respect tether radius constraint (PROP-M mode)
- Avoid known obstacles
- Produce dynamically feasible path

---

## 3.2 Local Planning

Local controller generates velocity commands:

Path + local obstacles  
-> Control law  
-> `/cmd_vel`

Must consider:

- Maximum curvature
- Maximum acceleration
- Slip sensitivity
- Narrow clearance

Preferred controller type:

Regulated Pure Pursuit or DWB variant with strict limits.

---

# 4. Constraint Enforcement

Constraint enforcement operates in parallel with planning.

It modifies or rejects goals that violate:

- Tether radius
- Maximum slope
- Energy constraints (future extension)
- Safety zones

In PROP-M mode:

Let:

R_max = 15 m

Constraint:

sqrt((X - X_lander)^2 + (Y - Y_lander)^2) <= R_max

If exceeded:

- Reject goal
- Trigger retreat behavior

Constraint logic must be deterministic.

---

# 5. Recovery Behaviors

Recovery is mandatory.

Defined behaviors:

- Clear local costmap
- Rotate in place
- Reverse short distance
- Retry path planning
- Abort mission segment

Recovery escalation:

1. Minor retry
2. Backtrack
3. Abort current segment
4. Signal mission failure

No infinite retry loops permitted.

---

# 6. Goal Handling

Goals originate from:

- Operator command
- Mission script
- Autonomous exploration logic

Goal states:

- Pending
- Executing
- Succeeded
- Failed
- Aborted

State transitions must be logged.

---

# 7. Science Action Integration (PROP-M Mode)

After each drive increment:

Mission executive triggers:

Science action  
-> Simulated soil probe  
-> Measurement duration timer  
-> Data logging  

Navigation remains paused during measurement.

Rover must be stationary during science action.

Velocity tolerance:

|v| < 0.01 m/s

---

# 8. Slip-Aware Navigation

If slip ratio exceeds threshold:

s > s_threshold

Navigation layer must:

- Reduce speed
- Increase cost of high-slip regions (future terrain map)
- Potentially retreat

Slip feedback is advisory to planner but mandatory to safety layer.

---

# 9. Map and Localization Strategy

Two operational modes:

## 9.1 Minimal Mode (PROP-M Emulation)

- Odometry + limited sensing
- No global SLAM
- Relative navigation only
- High drift tolerance

## 9.2 Modern Mode

- SLAM or localization against prior map
- Local + global costmaps
- Obstacle persistence

Localization drift must remain within:

< 2% of traveled distance (target)

---

# 10. Determinism Requirements

Autonomy must:

- Produce identical outputs under identical inputs
- Use fixed random seeds for simulation
- Avoid nondeterministic retries

Simulation regression must validate:

- Identical mission duration
- Identical path (within tolerance)
- Identical final pose (within tolerance)

---

# 11. Fault Handling

Autonomy must respond to:

- Low-level controller fault
- Sensor failure
- Estimation divergence
- Slip runaway
- Tether boundary violation

Response hierarchy:

Degrade  
-> Pause  
-> Retreat  
-> Abort  

No silent failures.

---

# 12. Logging Requirements

During autonomy execution:

Log:

- Goal poses
- Path length
- Recovery count
- Slip events
- Mission state transitions
- Execution time per segment

These metrics support:

- Regression testing
- Performance benchmarking
- Calibration

---

# 13. Acceptance Criteria

In mars_flat scenario:

- Reach 10 m waypoint within 2% distance error
- No recovery triggered
- Slip < 0.1

In mars_rocks scenario:

- Successfully navigate obstacle field
- <= 3 recoveries
- No boundary violation

In lander_tether_site scenario:

- Never exceed R_max
- Complete at least 5 drive-measure cycles
- Return within 0.5 m of start pose

---

# 14. Engineering Philosophy

Autonomy must be:

- Predictable
- Testable
- Constrained
- Conservative

It is optimizing for survivability and mission completion.
