# E03 - Static Sinkage Identification

## 1. Objective

Identify Bekker pressure–sinkage parameters under static loading.

This experiment estimates:

- kc (cohesive modulus)
- kphi (frictional modulus)
- n (sinkage exponent)

The purpose is to quantify how deeply the wheel penetrates the terrain
under known normal load.

This experiment isolates vertical soil behavior.
No longitudinal motion is permitted during measurement.

---

## 2. Test Philosophy

Terramechanics models are frequently overfit using traction data.
That is incorrect.

Bekker parameters must be identified from vertical loading only.

Static sinkage provides:

Load → sinkage relationship

W ≈ ∫ p(z) dA  
p(z) = (kc / b + kphi) z^n

We measure z for known W and solve for kc, kphi, n.

---

## 3. Scenario Requirements

Terrain:

- Flat
- Homogeneous
- No slope
- No compaction memory (fresh reset before each run)

Wheel:

- No rotation
- Zero commanded velocity
- No torque applied

Rover:

- Lowered gently into contact
- No lateral motion

---

## 4. Test Procedure

For each load condition:

1. Reset simulation.
2. Position wheel above surface.
3. Slowly lower until full static contact established.
4. Allow system to settle (≥ 3 seconds).
5. Record:
   - Normal load W
   - Sinkage depth z
6. Repeat for multiple load levels.

Minimum of 5 distinct loads required.

Load variation methods:

- Add mass to rover body (preferred in simulation)
OR
- Use vertical constraint force application (if supported)

---

## 5. Required Signals

- /joint_states
- Contact normal force (if available)
- /tf
- Wheel link pose (Z position)
- Ground reference height

Ground truth permitted in simulation for sinkage measurement.

---

## 6. Derived Quantities

Sinkage depth:

z = (wheel_center_z - r) - terrain_height

Where:

r = wheel radius

Normal load:

W = measured normal reaction force

If direct contact force unavailable:

Estimate:

W ≈ m_effective * g

with correction for load distribution across wheels.

---

## 7. Parameter Identification

Model:

W = k_eq * z^(n+1)

Where:

k_eq = function(kc, kphi, b)

Fit parameters:

- kc
- kphi
- n

Use nonlinear least squares.

Bounds:

0 ≤ kc ≤ 5000 Pa/m^(n+1)  
0 ≤ kphi ≤ 50000 Pa/m^(n+2)  
0.5 ≤ n ≤ 1.2  

Fit must not be unconstrained.

---

## 8. Loss Function

Minimize:

L = Σ (W_measured - W_model(z))²

Weight smaller z values slightly higher
to avoid overfitting large penetration outliers.

Optional normalized loss:

L_norm = Σ ((W_measured - W_model) / W_measured)²

---

## 9. Acceptance Criteria

Fit must satisfy:

- Monotonic increase of W with z
- R² ≥ 0.95
- Residuals randomly distributed
- No systematic bias

Physically plausible sinkage:

z < 0.5 * r

If penetration exceeds half radius,
model assumptions are invalid.

---

## 10. Outputs

analysis/calibration/outputs/<run_id>/E03/

- load_vs_sinkage.png
- fit_residuals.png
- fitted_parameters.json
- updated_terramechanics.yaml
- summary.md

---

## 11. Failure Modes

If data shows:

- Non-monotonic W or z -> contact detection issue
- Large oscillations -> insufficient settling time
- Excessively deep penetration -> unrealistic soil stiffness
- Near-zero penetration under high load -> friction-only contact model active

In such cases:

- Verify physics engine contact settings
- Verify gravity value
- Verify wheel geometry
- Verify terrain compliance

Do not force-fit parameters to broken data.

---

## 12. Engineering Rationale

Bekker parameters define:

- Sinkage
- Rolling resistance scaling
- Contact patch size
- Shear stress distribution

Without correct vertical calibration:

Traction model is physically inconsistent.

Static sinkage must be calibrated before incline testing (E04).

---

## 13. Notes

This experiment is quasi-static.

Dynamic effects must be negligible.

If dynamic oscillations are observed,
the simulation timestep or damping configuration must be reviewed.

Calibration requires controlled, stable measurements.
Not visually convincing behavior.
