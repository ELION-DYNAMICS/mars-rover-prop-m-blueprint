# PyBullet Simulation Architecture

This document defines the PyBullet-based simulation environment for the
Mars Rover Prop-M Blueprint.

PyBullet is used for:

- Rapid dynamics prototyping
- Terramechanics model validation
- Controller tuning under controlled physics
- Batch parameter sweeps
- Slip and traction analysis

PyBullet is NOT the primary ROS integration platform.
It is a controlled physics laboratory.

---

# 1. Purpose and Scope

PyBullet provides:

- Direct physics engine access
- Deterministic stepping
- Fine control over contact forces
- Easier force injection than Gazebo

It is especially useful for:

- Slip modeling validation
- Wheel–soil interaction experiments
- Parameter identification
- Sensitivity analysis

---

# 2. Simulation Architecture

Components:

URDF  
-> PyBullet physics engine  
-> Custom force model (terramechanics)  
-> Python control loop  
-> Logging  

ROS integration optional via bridge layer.

Preferred architecture:

Standalone physics core  
-> optional ROS bridge for testing  

---

# 3. Physics Engine Configuration

Physics parameters must be explicitly defined:

- timeStep (Δt)
- gravity vector
- solver iterations
- contact ERP
- contact CFM

Recommended baseline:

Δt = 0.001 s  
Fixed time stepping  
Deterministic mode enabled  

Real-time mode disabled for regression runs.

---

# 4. Rover Model Import

URDF must include:

- Accurate mass distribution
- Collision geometry
- Joint limits
- Wheel inertia

PyBullet ignores some advanced URDF features.
Verify:

- Joint axis orientation
- Inertia alignment
- Center of mass placement

Incorrect inertia results in unstable torque behavior.

---

# 5. Wheel-Ground Interaction Strategy

Two operating modes:

---

## 5.1 Native Coulomb Friction Mode

Use built-in friction model:

- lateralFriction
- spinningFriction
- rollingFriction

Suitable for:

- Baseline kinematic validation
- Control tuning
- Straight-line testing

Limitations:

- No sinkage
- No shear stress buildup
- No slip-dependent traction curve

---

## 5.2 Custom Terramechanics Mode

Override default traction:

Procedure:

1. Disable strong lateral friction
2. Compute slip ratio s
3. Compute sinkage via Bekker
4. Compute shear stress via Wong
5. Compute traction force F_x
6. Apply external force at wheel contact

Force application:

applyExternalForce(
    bodyUniqueId,
    linkIndex,
    force=[F_x, 0, 0],
    position=contact_point,
    flags=WORLD_FRAME
)

This enables:

Wheel torque  
-> Slip  
-> Shear stress  
-> Traction force  
-> Vehicle motion  

Physically consistent loop.

---

# 6. Slip Computation

Compute slip ratio:

s = (r ω - v) / max(|r ω|, ε)

Where:

r ω -> wheel peripheral speed  
v   -> body linear velocity  

Velocity extracted from:

getBaseVelocity()

Slip must be computed per wheel.

---

# 7. Contact Patch Approximation

PyBullet does not model deformable soil.

Approximate contact area:

A_contact ≈ b * l_contact

Where:

b = wheel width  
l_contact estimated from sinkage depth  

Simplified:

l_contact ≈ 2 sqrt(r z)

Used for shear integration.

---

# 8. Control Loop Structure

Typical loop:

while sim_running:

    read joint states
    compute slip
    compute traction
    compute torque command
    apply torque
    stepSimulation()
    log data

Loop frequency:

≥ 500 Hz recommended

Controller must operate on fixed timestep.

---

# 9. Determinism

For regression:

- Fixed timestep
- No GUI mode
- Fixed random seed
- No asynchronous threads

Simulation output must be identical between runs.

---

# 10. Data Logging

Log at each timestep:

- Position
- Orientation
- Wheel velocity
- Slip ratio
- Traction force
- Torque command
- Sinkage estimate

Export to:

CSV or structured JSON

Batch experiments must include:

run_metadata.json

---

# 11. Parameter Sweep Framework

PyBullet is ideal for parameter exploration.

Example sweep dimensions:

- kc
- kφ
- n
- c
- φ
- K
- wheel torque limits

For each run:

Compute:

- Distance traveled
- Energy consumption proxy
- Average slip
- Maximum slip
- Sinkage depth

Use for:

Calibration and model validation.

---

# 12. Validation Experiments

Minimum experiments:

1. Straight-line traction test
2. Incline climb test
3. Torque ramp test
4. Slip saturation curve
5. Differential steering under slip

Compare:

Measured v_actual  
vs  
Predicted v_model  

Error must remain bounded.

---

# 13. Limitations

PyBullet does NOT model:

- Granular flow
- Soil compaction memory
- Plastic deformation
- Soil displacement buildup

Terramechanics model compensates mathematically.

For high-fidelity soil physics:

DEM simulation required.

---

# 14. When to Use PyBullet

Use PyBullet when:

- Testing new slip formulations
- Evaluating controller stability under force perturbations
- Running thousands of batch experiments
- Debugging force inconsistencies

Do NOT use PyBullet for:

- Full ROS stack validation
- Navigation integration testing
- Mission-level regression

That belongs in Gazebo.

---

# 15. Engineering Discipline

PyBullet is a physics sandbox.

All parameter changes must be:

- Logged
- Versioned
- Justified

Never tune until it “looks good.”

Always tune against quantitative metrics.
