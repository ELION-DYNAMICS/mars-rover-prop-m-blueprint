# E04 - Incline Climb Force Balance Validation

## 1. Objective

Validate terramechanics parameters under inclined terrain.

This experiment verifies consistency between:

- Bekker sinkage model
- Wong shear stress model
- Rolling resistance model
- Slip behavior under load

The purpose is not to re-fit all parameters blindly.
It is to validate force balance under slope conditions
and refine rolling resistance and traction saturation.

---

## 2. Physical Principle

On an incline of angle θ:

Gravitational component opposing motion:

F_gravity = m g sin(θ)

Normal load:

W = m g cos(θ)

Net traction must satisfy:

F_x ≥ F_gravity + F_rr

Where:

F_rr = rolling resistance force

If the rover climbs steadily (a ≈ 0):

F_x ≈ F_gravity + F_rr

This is a direct validation of the traction envelope.

---

## 3. Scenario Requirements

Terrain:

- Uniform slope
- Known incline angle θ
- Homogeneous soil
- No obstacles

Test slopes:

- 5°
- 10°
- 15°
- 20° (optional upper bound)

Slope must be stable and deterministic.

---

## 4. Test Procedure

For each slope:

1. Reset simulation.
2. Position rover at base of incline.
3. Apply constant forward torque or velocity command.
4. Maintain steady climb for ≥ 5 meters.
5. Record steady-state segment.

No steering.

No contact events.

No tether constraints active.

---

## 5. Required Signals

- /joint_states
- /wheel/torque_command
- /wheel/slip_estimate
- /odometry/filtered
- /imu/data
- /cmd_vel_safe
- /tf

Ground truth (simulation only):

- /ground_truth/pose

Slope angle must be known from scenario configuration.

---

## 6. Derived Quantities

Actual velocity:

v_actual = derivative of position along slope

Acceleration:

a = derivative of v_actual

Slip:

s = (r ω - v_actual) / max(|r ω|, ε)

Estimated traction force:

F_x = m (a + g sin(θ))

Rolling resistance:

F_rr ≈ F_x - m g sin(θ)

If steady-state:

a ≈ 0  
F_x ≈ m g sin(θ) + F_rr

---

## 7. Validation Targets

At steady-state:

1. Predicted traction (from Wong model)  
   must match measured traction within tolerance.

2. Slip must increase with slope angle.

3. There must exist a critical slope angle  
   beyond which rover cannot climb steadily.

---

## 8. Parameter Refinement

E04 may refine:

- Rolling resistance coefficient (k_rr)
- Slip saturation parameter (s0)
- Shear deformation modulus (K)

Primary refinement target:

k_rr

Procedure:

Minimize:

L = Σ (F_measured - F_model)^2

Across all tested slopes.

---

## 9. Acceptance Criteria

For each slope:

Steady-state climb achieved if:

a ≈ 0  
Slip stable (no oscillation)  

Force balance consistency:

|F_model - F_measured| / F_measured < 0.15

Slip behavior:

s increases monotonically with θ

Maximum climb angle must be physically plausible.

If rover climbs unrealistic slopes (>30°)  
with low slip, soil model is incorrect.

---

## 10. Outputs

analysis/calibration/outputs/<run_id>/E04/

- slope_or_slip.png
- slope_or_required_force.png
- traction_model_comparison.png
- updated_terramechanics.yaml
- summary.md

---

## 11. Failure Modes

If:

- Rover climbs high slopes with near-zero slip -> friction-only contact active
- Slip oscillates strongly -> control instability
- Rover stalls at low slope angles (<5°) -> traction underestimated
- Rolling resistance negative -> sign error

Investigate:

- Gravity vector
- Mass configuration
- Wheel radius
- Slope angle definition
- Slip calculation

Do not adjust parameters to hide structural errors.

---

## 12. Engineering Rationale

Incline climb is the first environment where:

- Vertical load changes
- Shear stress increases
- Slip regime shifts
- Rolling resistance scales with sinkage

It validates the full terramechanics stack under realistic loading.

If E04 passes:

The model is internally consistent.

If it fails:

The system is not physically coherent.

---

## 13. Position in Calibration Sequence

Order is mandatory:

E01 – Slip baseline  
E02 – Traction envelope  
E03 – Static sinkage  
E04 – Incline validation  

Skipping steps invalidates conclusions.

This experiment is the final physical consistency check
before parameters are promoted to runtime configuration.
