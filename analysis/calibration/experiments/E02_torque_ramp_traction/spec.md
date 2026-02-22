# E02 – Torque Ramp Traction Identification

## 1. Objective

Identify the traction–slip relationship under controlled torque ramp.

This experiment estimates:

- Shear deformation modulus (K)
- Cohesion (c)
- Effective friction angle (φ)
- Slip saturation parameter (s0)
- Practical traction envelope

Results update:

- terramechanics_defaults.yaml
- control_defaults.yaml (torque_max refinement)
- estimator slip inflation thresholds

---

## 2. Hypothesis

Under increasing wheel torque:

1. Slip initially grows approximately linearly.
2. Traction force increases.
3. Traction saturates.
4. Additional torque increases slip but not forward acceleration.

This defines the traction curve.

Mathematically:

τ(j) = (c + σ tan(φ)) (1 - exp(-j / K))

and practical form:

F_x ≈ F_max (1 - exp(-s / s0))

---

## 3. Dataset Requirements

### 3.1 Scenario

- Terrain: flat, homogeneous
- No obstacles
- No tether constraint
- No steering (pure straight-line)

### 3.2 Execution Profile

1. Start at rest
2. Apply torque ramp:
   τ(t) increases linearly from 0 to τ_max
3. Maintain τ_max for short duration
4. Stop

No velocity command control during ramp.
Direct torque control mode required.

---

## 4. Required Signals

- /joint_states
- /wheel/torque_command
- /wheel/slip_estimate
- /odometry/filtered
- /imu/data
- /cmd_vel_safe (for verification)
- /tf

Ground truth (simulation only):

- /ground_truth/pose

---

## 5. Derived Quantities

Wheel torque:
τ_wheel = measured torque command

Wheel angular velocity:
ω = mean(ω_left, ω_right)

Ideal velocity:
v_ideal = r * ω

Actual velocity:
v_actual = derivative of position

Slip:
s = (v_ideal - v_actual) / max(|v_ideal|, ε)

Longitudinal force estimate:

F_x ≈ m * a

Where:
a = derivative of v_actual

(Preferably computed using filtered acceleration.)

---

## 6. Fit Parameters

Primary:

- cohesion_c_Pa
- friction_phi_deg
- shear_deformation_K_m

Secondary:

- slip_saturation_s0
- effective_max_traction_N

Optional:

- rolling resistance coefficient k_rr

---

## 7. Loss Function

Fit traction model:

F_model(s) = F_max (1 - exp(-s / s0))

Minimize:

L = || F_measured - F_model ||²

Where:

F_measured = m * a

Weight low-slip region more heavily:

w(s) = 1 / (1 + s)

Total loss:

L_total = Σ w(s_i) (F_i - F_model_i)²

---

## 8. Acceptance Criteria

Curve must exhibit:

- Monotonic traction increase
- Clear saturation region
- Physically plausible F_max

Parameter bounds:

0 ≤ c ≤ 2000 Pa  
20° ≤ φ ≤ 45°  
0.001 ≤ K ≤ 0.05 m  

Slip saturation:

0.10 ≤ s0 ≤ 0.40  

If parameters fall outside bounds,
investigate data integrity before accepting fit.

---

## 9. Outputs

analysis/calibration/outputs/<run_id>/E02/

- traction_curve.png
- slip_vs_force.png
- fitted_parameters.json
- updated_terramechanics.yaml
- summary.md

---

## 10. Report Requirements

Report must include:

- Dataset reference (run_id)
- Mass assumption used
- Slip range tested
- F_max estimate
- Parameter confidence
- Observed anomalies

---

## 11. Failure Modes

If traction curve:

- Oscillates strongly -> control instability
- Does not saturate -> torque limit too low
- Shows decreasing traction at high slip -> numerical noise
- Produces negative traction under forward torque -> sign error

Do not force-fit parameters.

Root cause must be identified before updating defaults.

---

## 12. Engineering Rationale

This experiment quantifies the soil-wheel interaction envelope.

Without E02:

- Slip thresholds are arbitrary
- Torque limits are guesswork
- Terramechanics model lacks physical grounding

E02 defines the traction ceiling of the rover.

It is mandatory before incline testing (E04).
