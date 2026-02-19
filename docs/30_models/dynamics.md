# Dynamics Model

This document defines the dynamic model of the rover platform used for:

- Low-level controller design
- Torque budgeting
- Simulation fidelity
- Power estimation
- Slip and soil interaction coupling

The dynamic model extends the kinematic model by incorporating mass, inertia, actuator limits, and external forces.

All modeling assumes planar motion unless explicitly stated.

---

# 1. System Definition

The rover is modeled as a rigid body with two driven wheels and passive support elements.

State vector:

x = [X, Y, θ, v, ω]

Where:
X, Y = position in inertial frame  
θ = yaw angle  
v = longitudinal velocity  
ω = yaw rate  

Control inputs:

τ_l, τ_r = left and right wheel torques

---

# 2. Physical Parameters

m      = rover mass [kg]  
I_z    = yaw moment of inertia about vertical axis [kg·m²]  
r      = wheel radius [m]  
L      = wheel separation [m]  
J_w    = wheel inertia [kg·m²]  
b      = viscous friction coefficient (drive system)  
μ      = wheel-ground friction coefficient  

All values must be defined in hardware specification and mirrored in simulation.

---

# 3. Longitudinal Dynamics

Sum of forces along body x-axis:

m v̇ = F_r + F_l - F_res

Where:

F_r = τ_r / r  
F_l = τ_l / r  

F_res includes:

- Rolling resistance
- Soil deformation resistance
- Aerodynamic drag (negligible on Mars at low speed)

Rolling resistance approximation:

F_rr = C_rr m g

Total:

v̇ = (1/m) [ (τ_r + τ_l)/r - F_rr - F_soil ]

---

# 4. Rotational Dynamics

Yaw moment about center:

I_z ω̇ = (L/2)(F_r - F_l)

Substitute wheel forces:

ω̇ = (L / (2 I_z r)) (τ_r - τ_l)

---

# 5. Wheel Dynamics

Each wheel:

J_w ω̇_w = τ_motor - τ_ground - b ω_w

Ground reaction torque:

τ_ground = r F_longitudinal

Coupled through slip and traction model.

---

# 6. Actuator Model

Motor torque:

τ_motor = K_t i

Electrical model:

V = R i + L di/dt + K_e ω_w

For simulation simplification:

τ_motor = τ_cmd limited by:

- τ_max
- current limits
- thermal envelope

Torque saturation must be modeled.

---

# 7. Traction Limits

Maximum transferable longitudinal force:

|F_long| ≤ μ N

Where:

N = normal force ≈ m g / 2 (per wheel, flat terrain)

If:

|τ/r| > μ N

Then slip occurs and traction is capped.

This introduces nonlinear dynamics.

---

# 8. Combined State-Space Representation

Define state:

x = [v, ω]

Then:

v̇ = (1/m) [ (τ_r + τ_l)/r - F_res ]

ω̇ = (L / (2 I_z r)) (τ_r - τ_l)

This forms a nonlinear system due to:

- traction limits
- soil resistance
- actuator saturation

---

# 9. Energy Model

Mechanical power:

P_mech = τ_r ω_r + τ_l ω_l

Electrical power (approx.):

P_elec ≈ V i

Energy consumption integral:

E = ∫ P_elec dt

Used for mission endurance estimation.

---

# 10. Slope Effects

For terrain slope angle α:

Effective gravitational component:

F_slope = m g sin(α)

Normal force reduction:

N = m g cos(α)

This modifies:

- traction limit
- rolling resistance

Longitudinal equation becomes:

m v̇ = (τ_r + τ_l)/r - F_rr - F_slope

---

# 11. Stability Considerations

Low-speed planetary rovers operate in quasi-static regime.

Dominant effects:

- traction limits
- rolling resistance
- actuator saturation

Inertial coupling is secondary but included for:

- rotation-in-place validation
- acceleration modeling
- simulation realism

---

# 12. Validity Domain

Model valid for:

- v < 1.5 m/s
- moderate slopes (< 20°)
- rigid-body chassis assumption
- no suspension articulation modeling

Higher-fidelity modeling requires:

- Multi-body dynamics
- Soil deformation coupling (see terramechanics.md)
- Compliance modeling

---

# 13. Verification Criteria

Simulation must reproduce:

- Acceleration under constant torque
- Deceleration under rolling resistance only
- Symmetric response left/right torque
- Stable rotation with τ_l = -τ_r

Acceptable deviation:

- <5% acceleration error vs analytical prediction
- <3% steady-state velocity error under constant torque

---

# 14. Relationship to Kinematic Layer

Kinematics describes:

(X, Y, θ)

Dynamics determines:

(v, ω) evolution

Control layer operates on torque commands, not velocity directly.

Velocity control must sit above torque control in hierarchy.

---

# 15. Implementation Notes

- All parameters stored in YAML
- Simulation and hardware must use identical parameter sets
- Torque saturation must be enforced before physics update
- Logging of τ_l, τ_r, v, ω required for regression analysis


