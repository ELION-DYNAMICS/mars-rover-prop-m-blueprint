# E01 – Straight Line Slip Identification

## 1. Objective

Identify longitudinal slip behavior under controlled straight-line motion.

This experiment estimates:

- Effective slip ratio bias
- Slip variance under nominal load
- Initial traction saturation parameter (s0)
- Rolling resistance proxy under flat terrain

The results inform:

- Terramechanics slip regime thresholds
- EKF slip-aware covariance inflation
- Control slip containment thresholds

---

## 2. Hypothesis

Under flat terrain and constant commanded velocity:

Ideal velocity (kinematic)  
≠  
Measured velocity (actual displacement)

The difference is primarily explained by slip:

s = (r ω - v_actual) / max(|r ω|, ε)

Slip should remain bounded in nominal terrain:

0.05 ≤ s ≤ 0.25

If outside this range, model or control parameters are inconsistent.

---

## 3. Dataset Requirements

### 3.1 Scenario

- Scenario: `mars_flat`
- Terrain: flat, homogeneous
- No obstacles
- No tether constraint interaction
- Constant normal load

### 3.2 Execution Conditions

- Fixed random seed
- Fixed simulation step size
- Constant velocity command (no ramps during measurement window)

Command profile:

1. Ramp to target velocity
2. Hold constant velocity for ≥ 10 seconds
3. Stop

### 3.3 Target Velocity

Test at multiple speeds:

- 0.05 m/s
- 0.10 m/s
- 0.15 m/s (optional if stable)

---

## 4. Required Signals (ICD-compliant)

Must be available in dataset:

- /joint_states
- /wheel/odometry_raw
- /odometry/filtered
- /imu/data
- /wheel/slip_estimate (if available)
- /cmd_vel_safe
- /tf

Ground truth (simulation only, evaluation use only):

- /ground_truth/pose

---

## 5. Derived Quantities

Compute:

Wheel angular velocity:
ω = mean(ω_left, ω_right)

Ideal wheel linear speed:
v_ideal = r * ω

Actual velocity:
v_actual = derivative of ground truth X
OR
v_actual = odometry position derivative (if no ground truth)

Slip ratio:
s = (v_ideal - v_actual) / max(|v_ideal|, ε)

Filter out transient ramp segments.

Only analyze steady-state window.

---

## 6. Loss Function

Primary objective:

Minimize variance of slip during steady-state:

L1 = Var(s)

Secondary objective:

Minimize bias between predicted and observed slip:

L2 = |mean(s_model - s_measured)|

Optional traction curve fit:

Fit:
v_actual = v_ideal * (1 - s_eff)

Minimize:

L3 = || v_measured - v_model ||²

Total loss:

L = w1 L1 + w2 L2 + w3 L3

Weights must be documented.

---

## 7. Acceptance Criteria

For flat terrain baseline:

Mean slip:
0.05 ≤ mean(s) ≤ 0.20

Slip variance:
Var(s) < 0.01

Velocity tracking error:
|v_ideal - v_actual| / v_ideal < 0.20

No oscillatory slip behavior.

No divergence.

---

## 8. Outputs

Generate:

- Updated slip thresholds in terramechanics config
- Suggested EKF Q inflation parameters
- Suggested control slip threshold adjustments

Export:

analysis/calibration/outputs/<run_id>/E01/
  - slip_timeseries.png
  - slip_histogram.png
  - summary.json
  - updated_terramechanics.yaml (if applicable)
  - updated_estimator.yaml (if applicable)

---

## 9. Report Requirements

Report must include:

- Dataset reference (run_id)
- Git commit hash
- Commanded velocity
- Mean slip
- Slip variance
- Interpretation
- Recommendation

---

## 10. Failure Modes

If:

- Slip > 0.40 consistently
- Slip negative (under braking regime unexpectedly)
- High-frequency oscillation present

Then:

- Inspect wheel radius consistency
- Inspect encoder scaling
- Inspect physics contact configuration
- Inspect control oscillation

Do not tune parameters blindly.

Investigate root cause.

---

## 11. Engineering Rationale

Straight-line slip identification isolates:

- Wheel-ground interaction
- Velocity estimation fidelity
- Control stability

Without this experiment:

- Terramechanics cannot be trusted
- Estimation tuning is guesswork
- Control slip containment is arbitrary

This experiment is mandatory before E02–E04.
