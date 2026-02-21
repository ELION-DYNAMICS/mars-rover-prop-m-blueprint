# Webots Simulation Architecture

This document defines the Webots-based simulation environment for the
Mars Rover Prop-M Blueprint.

Webots is used for:

- Deterministic robotics simulation
- Rapid full-stack integration testing
- Sensor realism validation
- Education-grade reproducibility
- Alternative physics cross-check

Webots is not the primary system simulator.
It is a controlled robotics execution platform with strong ROS 2 integration.

---

# 1. Purpose and Role in the Stack

Webots complements:

Gazebo -> large-scale system simulation  
PyBullet -> force-level physics experimentation  

Webots provides:

- Stable multi-platform support
- Clean robot–world separation
- Built-in sensor models
- Deterministic time stepping
- Reliable ROS 2 controller interface

Use cases:

- End-to-end autonomy validation
- Sensor noise characterization
- Repeatable regression tests
- Lightweight CI simulation

---

# 2. Simulation Architecture Overview

Components:

URDF / PROTO definition  
-> Webots physics engine  
-> Device nodes (motors, sensors)  
-> ROS 2 interface layer  
-> Autonomy stack  
-> Logging  

Separation rule:

Webots handles:
- Physics
- Sensors
- Actuation devices

ROS handles:
- Estimation
- Planning
- Control logic
- Mission management

No autonomy logic inside Webots controller scripts.

---

# 3. Rover Model Definition

The rover must be defined either as:

- URDF imported via webots_ros2
OR
- Native PROTO file

Model must include:

- Accurate mass distribution
- Correct inertia tensors
- Wheel geometry
- Joint limits
- Collision shapes

Center of gravity must be validated.

Incorrect inertia produces unrealistic pitch/roll behavior.

---

# 4. Physics Configuration

Webots physics parameters:

- basicTimeStep
- world gravity
- solver parameters
- contact properties

Recommended baseline:

basicTimeStep = 1 ms – 2 ms  
Fixed-step simulation  
No real-time drift during regression runs  

Friction parameters must reflect:

- Baseline Coulomb friction
- No unrealistic infinite grip

If terramechanics model used:

Wheel-ground friction reduced
Custom traction logic applied in control layer

---

# 5. Wheel-Ground Interaction Modes

## 5.1 Native Contact Model

Use Webots friction model:

- μ_longitudinal
- μ_lateral

Suitable for:

- Navigation validation
- Control stability testing
- Straight-line performance evaluation

Limitations:

- No soil sinkage
- No shear stress buildup
- No slip saturation curve

---

## 5.2 Terramechanics-Augmented Mode

Approach:

- Read wheel angular velocity
- Estimate slip ratio
- Compute traction force via Bekker + Wong model
- Adjust effective velocity or torque command

Because Webots does not support deformable terrain natively:

Terramechanics must be implemented in:

- Controller layer
OR
- External force injection mechanism

This mode prioritizes traction realism over visual fidelity.

---

# 6. Sensor Modeling

Webots provides built-in devices:

- InertialUnit
- GPS (disabled in PROP-M emulation)
- Gyro
- Camera
- Lidar
- TouchSensor (for contact bars)

All sensors must include:

- Noise configuration
- Update rate specification
- Covariance matching estimator assumptions

Noise must be parameterized and version-controlled.

---

# 7. Contact Detection (PROP-M Mode)

Contact bars modeled using:

TouchSensor or distance threshold logic.

On contact:

Publish ROS topic  
Trigger low-level control override  
Log event  

Latency must remain bounded.

Target:

< 10 ms detection delay

---

# 8. Time Handling

Webots provides simulation time.

All ROS nodes must use:

use_sim_time = true

No wall-clock dependencies allowed.

Regression tests must operate in fixed-step mode.

---

# 9. ROS 2 Integration

Recommended interface:

webots_ros2

Bridges:

- Joint state publishing
- Sensor topics
- Motor velocity commands
- TF broadcasting

Control structure:

ROS sends velocity command  
-> Webots motor device  
-> Physics step  
-> Sensor feedback  
-> ROS estimator  

No direct bypassing of control stack.

---

# 10. Determinism and Regression

For reproducibility:

- Fixed random seed
- Fixed physics step
- Identical world file
- Identical parameters

Regression must validate:

- Final pose within tolerance
- Identical mission state transitions
- Bounded slip variation

---

# 11. World Definitions

World files must include:

- Terrain geometry
- Lander reference object (PROP-M mode)
- Lighting
- Gravity vector
- Material definitions

No rover-specific parameters embedded in world file.

World defines terrain.
Rover defines behavior.

---

# 12. Performance Validation

Minimum validation scenarios:

mars_flat  
mars_rocks  
lander_tether_site  

Acceptance criteria:

Straight-line error < 1%  
Heading drift < 2°  
No boundary violation  
Controlled recovery behavior  

---

# 13. Simulation Fidelity Limits

Webots does not simulate:

- Soil plastic deformation
- Granular flow
- Deep sinkage physics
- Soil memory effects

For high-fidelity soil interaction:

Use PyBullet with custom force model  
or external DEM tools.

Webots is suitable for:

- System integration
- Navigation validation
- Sensor noise evaluation

---

# 14. When to Use Webots

Use Webots when:

- Testing full ROS stack
- Verifying estimator stability
- Validating behavior trees
- Running lightweight CI tests
- Teaching or demonstrating architecture

Do not use Webots for:

- Detailed terramechanics validation
- Force-level experimental physics
- High-load torque studies

---

# 15. Engineering Discipline

Webots configuration must:

- Be version controlled
- Use parameter files
- Avoid hidden tuning
- Log every mission run

Simulation exists to falsify assumptions.

If behavior improves only in one simulator,
investigate why.
