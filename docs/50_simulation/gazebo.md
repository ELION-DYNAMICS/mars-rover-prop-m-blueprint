# Gazebo Simulation Architecture

This document defines the simulation architecture for the Mars Rover Prop-M Blueprint.

Simulation is not for visualization.

It is used for:

- Control validation
- Estimation tuning
- Terramechanics modeling
- Regression testing
- Mission verification

Simulation must be deterministic, parameterized, and reproducible.

---

# 1. Simulation Platform

Target:

Gazebo (Ignition / Harmonic recommended)

Reasons:

- Modern physics engine (DART or TPE)
- Native ROS 2 integration
- Deterministic stepping support
- Headless operation capability
- World and sensor plugin flexibility

Simulation must support:

- Headless batch execution
- Seeded randomness
- Programmatic reset
- Metric extraction

---

# 2. Simulation Architecture Overview

Components:

URDF/Xacro  
-> Gazebo physics engine  
-> Sensor plugins  
-> ros_gz_bridge  
-> ROS 2 nodes  
-> Logging (MCAP)

Strict separation:

Gazebo handles physics  
ROS handles autonomy  

No control logic inside Gazebo plugins.

---

# 3. Rover Model (URDF)

The URDF must include:

- Correct mass and inertia tensors
- Accurate wheel radius and width
- Proper collision geometry
- Joint definitions for wheels
- Transmission definitions

Mass properties must reflect:

Total rover mass  
Wheel mass  
Center of gravity  

Incorrect inertia causes unstable control tuning.

---

# 4. Physics Engine Configuration

Critical parameters:

- Step size (Δt)
- Real-time factor
- Solver iterations
- Contact surface properties

Recommended baseline:

Physics step: 0.001–0.002 s  
Update rate: 500–1000 Hz internal  
Real-time factor: 1.0 (or locked-step in CI)

Contact parameters:

- Friction coefficient μ
- Restitution
- Contact stiffness

These must be consistent with terramechanics assumptions.

---

# 5. Wheel-Ground Interaction

Baseline mode:

Gazebo friction model (Coulomb friction)

Advanced mode:

Custom plugin applying:

- Bekker sinkage
- Wong shear model
- Slip-dependent traction force

In advanced mode:

Wheel torque  
-> Compute slip ratio  
-> Compute F_x  
-> Override longitudinal force  

Gazebo contact model must not double-count friction.

Only one traction model should dominate.

---

# 6. Sensor Simulation

## 6.1 IMU

Simulated IMU must include:

- Gaussian noise
- Bias drift
- Configurable covariance

Noise must be parameterized.

---

## 6.2 Wheel Encoders

Wheel angular velocity derived from joint state.

Optional:

Add quantization + noise.

---

## 6.3 Contact Sensors (PROP-M Mode)

Binary or analog contact triggers.

Contact event  
-> Publish ROS topic  
-> Mission layer reacts

Contact response latency must be measurable.

---

## 6.4 Optional Sensors (Modern Mode)

- LiDAR
- Camera
- Depth sensor

Must operate under same clock as physics.

---

# 7. Time and Clock Handling

Simulation must publish:

`/clock`

All ROS nodes must use simulated time.

No system wall time allowed in simulation mode.

Deterministic stepping required for regression tests.

---

# 8. Determinism Requirements

Given:

Same random seed  
Same world file  
Same parameters  

Simulation must produce:

- Identical final pose (within tolerance)
- Identical slip events
- Identical recovery count

Random seed must be set in:

- Physics engine
- Sensor noise generators

---

# 9. World Definitions

Worlds stored in:

`scenarios/*`

Each world must include:

- Terrain geometry
- Material parameters
- Lighting
- Lander reference model (PROP-M mode)

No hard-coded parameters inside rover model.

World defines terrain.

Rover defines mechanics.

---

# 10. Tether Constraint Simulation (PROP-M Mode)

The tether is modeled logically, not physically.

Approach:

Monitor rover position relative to lander.

If:

distance > R_max

Then:

- Block forward commands
- Trigger retreat

Optional advanced mode:

Simulate tether as spring constraint:

F_tether = -k_t (d - R_max)

Only if mechanical realism desired.

Baseline implementation remains logical constraint.

---

# 11. Data Logging

Each simulation run must generate:

- MCAP bag
- run_metadata.json
- metrics.json

Metrics include:

- Total distance
- Slip events
- Recovery count
- Mission duration
- Energy estimate (optional)

Simulation must terminate cleanly and export data automatically.

---

# 12. Regression Testing

CI simulation must:

- Run headless
- Use fixed seed
- Complete within defined time limit
- Evaluate metrics against thresholds

Test scenarios:

mars_flat  
mars_rocks  
mars_dunes  
lander_tether_site  

Failure conditions:

- Boundary violation
- Divergence
- Excessive slip
- Unbounded oscillation

---

# 13. Validation Strategy

Before trusting autonomy:

Validate subsystems independently:

1. Straight-line drive test  
2. Circular trajectory test  
3. Rotation-in-place symmetry  
4. Controlled slip injection  
5. Contact-triggered reversal  

Only after subsystem validation proceed to full mission test.

---

# 14. Simulation or Reality Gap

Simulation does not perfectly model:

- Soil compaction memory
- Micro-slip
- Structural flex
- Temperature effects
- Electronics latency

Simulation is a validation tool.

It is not a substitute for hardware testing.

---

# 15. Engineering Discipline

No tuning directly inside Gazebo.

All parameters must live in:

- YAML configs
- URDF
- terramechanics parameters file

Simulation must remain transparent and reproducible.

If results change, cause must be traceable.
