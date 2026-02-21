# Verification and Validation (V&V)

This document defines the Verification and Validation framework
for the Mars Rover Prop-M Blueprint.

Verification answers:

-> Did we build the system correctly?

Validation answers:

-> Did we build the correct system?

Both are mandatory.

---

# 1. Scope

V&V applies to:

- Kinematics
- Terramechanics
- Low-level control
- Estimation
- Planning and autonomy
- Simulation environments
- Data logging

No subsystem is exempt.

---

# 2. Verification Strategy (Subsystem-Level)

Verification is performed at increasing levels:

Level 0 -> Mathematical Model Validation  
Level 1 -> Unit Testing  
Level 2 -> Integration Testing  
Level 3 -> Scenario-Based Testing  
Level 4 -> Regression Testing  

Each level must pass before moving upward.

---

# 3. Model Verification

## 3.1 Kinematics

Test:

Straight-line drive  
-> Compare predicted or simulated displacement  

Acceptance:

< 1% position error over 10 m  

Rotation in place  
-> Heading error < 2°

---

## 3.2 Terramechanics

Test:

Controlled torque ramp  
-> Measure slip or predicted slip  

Acceptance:

Slip prediction error < 5%  

Incline test  
-> Compare required torque or model  

---

## 3.3 Dynamics

Test:

Apply known torque  
-> Verify acceleration response  

Acceptance:

Acceleration error < 5%

---

# 4. Control Verification

## 4.1 Wheel Velocity Tracking

Step input test:

Desired ω  
-> Measure tracking response  

Acceptance:

Rise time within specification  
Overshoot < 10%  
Steady-state error < 5%

---

## 4.2 Slip Containment

Induce slip:

Monitor torque scaling behavior  

Acceptance:

Slip ratio remains below defined safety threshold.

---

# 5. Estimation Verification

## 5.1 Drift Test

Flat terrain, constant speed:

Measure drift accumulation  

Acceptance:

Drift < 1% over 10 m  

---

## 5.2 Covariance Consistency

Compute:

Normalized Estimation Error Squared (NEES)

Acceptance:

NEES within statistical bounds.

---

# 6. Autonomy Verification

## 6.1 Waypoint Reach Test

mars_flat:

Reach 10 m goal  

Acceptance:

Final pose error < 2%  

---

## 6.2 Obstacle Field

mars_rocks:

Navigate through obstacle field  

Acceptance:

<= 3 recoveries  
No boundary violations  

---

## 6.3 PROP-M Mission Loop

lander_tether_site:

Execute 5 drive-measure cycles  

Acceptance:

No tether violation  
Return within 0.5 m of start  

---

# 7. Validation Strategy (System-Level)

Validation ensures behavior matches mission intent.

Questions:

- Does the rover complete missions reliably?
- Does it behave conservatively?
- Does it remain stable under uncertainty?
- Are failures predictable?

Validation includes:

- Long-duration simulation runs
- Parameter variation testing
- Sensor noise injection
- Slip amplification scenarios

---

# 8. Regression Framework

All tests must run in CI.

Regression includes:

- Fixed random seed
- Headless simulation
- Automatic metrics extraction
- Threshold-based pass/fail

Metrics tracked:

- Distance traveled
- Average slip
- Maximum slip
- Recovery count
- Boundary violations
- Mission duration

If metrics drift:

-> Investigation required  
-> No silent degradation allowed  

---

# 9. Stress Testing

Stress scenarios include:

- High slip terrain
- Sensor dropout
- IMU bias injection
- Torque saturation
- Communication delay

System must:

Degrade gracefully  
Never enter unstable oscillation  

---

# 10. Traceability

Every requirement must map to:

-> Test case  
-> Acceptance criterion  
-> Logged metric  

Example:

Requirement: “Tether radius ≤ 15 m”  
Test: lander_tether_site scenario  
Metric: max_distance_from_lander  
Acceptance: ≤ 15.0 m  

All traceability documented.

---

# 11. Documentation Discipline

Every test must include:

- Description
- Parameters
- Expected behavior
- Measured outcome
- Version number

No undocumented tuning allowed.

---

# 12. Failure Handling Policy

When a test fails:

1. Reproduce with identical seed  
2. Identify subsystem responsible  
3. Correct root cause  
4. Re-run regression suite  
5. Document change  

No bypassing failing tests.

---

# 13. Performance Baselines

Baseline metrics must be recorded at:

v0.1  
v0.2  
v0.3  
v1.0  

Future changes must not degrade:

- Stability
- Drift performance
- Mission completion rate

Unless explicitly justified.

---

# 14. Engineering Philosophy

“Test what you fly, fly what you test.”
- NASA Engineering Principle

Testing is not a final step.
Testing is always continuous.

Every model assumption must be falsifiable.

Every improvement must be measurable.

Confidence does not come from visual plausibility.
Confidence comes from reproducibility, traceability, and quantified uncertainty.

Simulation is not trusted because it looks correct.
It is trusted only after it survives systematic falsification.

No change is accepted without:
-> measurable improvement
-> regression confirmation
-> documented rationale

Engineering rigor is enforced through repeatability, not optimism.
