# Kinematics Model

This document defines the rover kinematic model used in:
- State propagation
- Controller design
- Simulation validation
- Estimation tuning

Unless otherwise stated, the rover is modeled as a planar differential-drive platform.

---

# 1. Coordinate Frames

## 1.1 Frames (ROS 2 Convention)

- `map` : global inertial frame
- `odom` : locally drift-free frame
- `base_link` : rover body frame (origin at geometric center)
- `wheel_left`, `wheel_right` : wheel frames

Right-handed coordinate system:
- x forward
- y left
- z upward

Heading angle:
θ = yaw angle of `base_link` in `odom` frame

---

# 2. Geometric Parameters

Let:

r  = wheel radius [m]  
L  = wheel separation (track width) [m]  
ω_l = left wheel angular velocity [rad/s]  
ω_r = right wheel angular velocity [rad/s]  

---

# 3. Differential Drive Kinematics

## 3.1 Linear and Angular Velocity

Linear velocity of rover center:

v = (r / 2) (ω_r + ω_l)

Angular velocity (yaw rate):

ω = (r / L) (ω_r - ω_l)

---

## 3.2 Continuous-Time State Model

State vector:

x = [ X, Y, θ ]ᵀ

Where:
X, Y = position in `odom`
θ = heading angle

State equations:

Ẋ = v cos(θ)  
Ẏ = v sin(θ)  
θ̇ = ω

This model assumes:
- No lateral slip
- Pure rolling contact
- Planar terrain

---

# 4. Discrete-Time Model

For simulation and estimation (Δt timestep):

Xₖ₊₁ = Xₖ + vₖ cos(θₖ) Δt  
Yₖ₊₁ = Yₖ + vₖ sin(θₖ) Δt  
θₖ₊₁ = θₖ + ωₖ Δt  

Higher-order integration (RK4) recommended for simulation.

---

# 5. Instantaneous Center of Curvature (ICC)

When ω ≠ 0:

R = v / ω

The rover rotates about the ICC located at distance R from center.

Special cases:
- ω = 0 -> straight motion
- ω_l = -ω_r -> pure rotation

---

# 6. Wheel Velocity Inverse Kinematics

Given desired (v, ω):

ω_r = (1 / r) (v + (L/2) ω)  
ω_l = (1 / r) (v - (L/2) ω)

Used by:
- Velocity controller
- Nav2 command translation
- Safety layer

---

# 7. Non-Ideal Effects (First-Order Extensions)

## 7.1 Slip Ratio

Define longitudinal slip:

s = (r ω - v_wheel) / max(|v_wheel|, ε)

Where:
v_wheel = actual longitudinal velocity at wheel contact.

In presence of slip:

v_actual ≠ (r / 2)(ω_r + ω_l)

Slip estimation must be handled in:
- Estimation layer
- Terramechanics model

---

## 7.2 Lateral Slip (Unmodeled in Ideal Case)

Ideal model assumes:

v_y_body = 0

Real terrain introduces lateral velocity component.

This deviation is captured in:
- EKF covariance tuning
- Terramechanics extension model

---

# 8. Jacobians (For EKF)

State transition Jacobian F:

F = ∂f/∂x

F =

[ 1   0   -v sin(θ) Δt ]  
[ 0   1    v cos(θ) Δt ]  
[ 0   0        1       ]

Control Jacobian G:

G = ∂f/∂u

Where u = [v, ω]ᵀ

G =

[ cos(θ) Δt    0 ]  
[ sin(θ) Δt    0 ]  
[     0       Δt ]

Used in EKF propagation step.

---

# 9. Assumptions and Validity Domain

Valid when:

- |slope| < ~15°
- Low slip regime
- Moderate velocity (< 1 m/s typical Mars rover speeds)
- Planar terrain assumption acceptable

Outside this regime, use:
- Full dynamic model
- Terramechanics-based slip estimation

---

# 10. Relationship to Simulation

Simulation must:

- Use same r and L as model
- Publish wheel joint states
- Validate:
    - straight-line drift error
    - circular trajectory error
    - rotation-in-place symmetry

Acceptance criteria example:

- < 1% error in straight-line distance over 10 m
- < 2° heading error over 360° rotation

---

# 11. PROP-M Mode Notes

Original PrOP-M operated at low speeds with stop-measure cycles.

Therefore:
- v is near zero during measurement phase
- motion increments are discrete
- odometry drift accumulates between stops

This matches discrete-time formulation.

---

# Conclusion

This kinematic model defines:

- Control law mapping
- State propagation
- Estimation structure
- Simulation validation criteria

Dynamic and soil interaction effects are handled separately in:

30_models/dynamics.md  
30_models/terramechanics.md

