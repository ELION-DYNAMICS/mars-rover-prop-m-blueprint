# Terramechanics Model

This document defines the soil–wheel interaction model used for:

- Slip estimation
- Traction prediction
- Sinkage calculation
- Simulation realism
- Controller tuning in deformable terrain

The rover operates on deformable regolith-like soil.  
Pure rolling assumptions (see kinematics.md) are insufficient.

---

# 1. Modeling Scope

We model:

- Normal pressure distribution under wheel
- Sinkage depth
- Shear stress development along contact patch
- Longitudinal traction force
- Slip-dependent force saturation

We assume:
- Rigid wheel
- Homogeneous soil
- Low-speed regime (quasi-static approximation)
- No dynamic soil fluidization

---

# 2. Bekker Pressure–Sinkage Model

Bekker’s empirical relation describes normal stress vs. sinkage.

Pressure:

p(z) = (kc / b + kφ) z^n

Where:

p(z)  = normal pressure at depth z  
z     = sinkage depth [m]  
b     = wheel width [m]  
kc    = cohesive modulus [Pa/m^(n+1)]  
kφ    = frictional modulus [Pa/m^(n+2)]  
n     = sinkage exponent (dimensionless)

---

## 2.1 Total Normal Force

Wheel load W must balance integrated pressure:

W = ∫ p(z) dA

For practical implementation, approximate:

W ≈ k_eq * z^(n+1)

Solve numerically for z given known W.

This gives:
sinkage depth z for given terrain parameters.

---

# 3. Shear Stress Model (Wong)

Wong’s shear stress formulation describes traction generation.

Shear stress at contact:

τ(j) = (c + σ tan(φ)) (1 - exp(-j / K))

Where:

τ(j)  = shear stress at shear displacement j  
c     = soil cohesion [Pa]  
σ     = normal stress  
φ     = internal friction angle  
K     = shear deformation modulus [m]  
j     = shear displacement

---

## 3.1 Shear Displacement

For wheel rotation:

j(θ) = r (θ_0 - θ) - v / ω

Where:

θ_0  = entry angle  
θ    = local angle in contact patch  
r    = wheel radius  
v    = translational velocity  
ω    = wheel angular velocity  

This links slip to traction buildup.

---

# 4. Slip Ratio Definition

Slip ratio s is defined as:

s = (r ω - v) / max(|r ω|, ε)

Where:

r ω  = peripheral wheel speed  
v    = forward vehicle speed  
ε    = small constant to avoid division by zero  

Interpretation:

s = 0     = pure rolling  
0 < s < 1 = traction regime  
s = 1     = full slip (wheel spinning)  
s < 0     = braking slip  

For rover mobility analysis, typical operating regime:

0.05 < s < 0.25

Beyond that -> efficiency drops rapidly.

---

# 5. Longitudinal Traction Force

Total longitudinal force:

F_x = ∫ τ(j) dA

Practical approximation:

F_x ≈ A_contact * (c + σ tan(φ)) * (1 - exp(-s / s_0))

Where:

s_0 -> slip scaling factor derived from K

This captures:

- Initial linear traction buildup
- Saturation behavior
- Dependence on soil cohesion + friction

---

# 6. Rolling Resistance

Rolling resistance on deformable soil:

F_rr ≈ k_rr * W * (z / r)

Where:

W = wheel load  
z = sinkage  
r = radius  

Higher sinkage -> higher energy loss.

---

# 7. Parameters Table

| Parameter | Meaning | Typical Mars Regolith Range |
|-----------|----------|-----------------------------|
| kc        | cohesive modulus | 0 – 5 kPa/m^(n+1) |
| kφ        | frictional modulus | 100 – 1000 kPa/m^(n+2) |
| n         | sinkage exponent | 0.5 – 1.2 |
| c         | cohesion | 0 – 2 kPa |
| φ         | friction angle | 25° – 40° |
| K         | shear deformation modulus | 0.005 – 0.03 m |
| k_rr      | rolling resistance coeff | empirical |

Values depend heavily on site.

---

# 8. Force Balance on Wheel

Net longitudinal force:

F_net = F_x - F_rr

Vehicle acceleration:

m a = Σ F_net

In low-speed Mars rover regime:
quasi-static assumption often acceptable:

a ≈ 0  
F_x ≈ F_rr + grade resistance

---

# 9. Integration with Kinematics

Ideal kinematic velocity:

v_ideal = (r / 2)(ω_r + ω_l)

Actual velocity:

v_actual = v_ideal (1 - s)

Thus:

Odometry overestimates motion when slip > 0  
→ EKF must incorporate slip model  
→ simulation must inject slip-dependent velocity reduction  

---

# 10. Calibration Strategy

Calibration must be data-driven.

## Step 1 -> Controlled Straight Runs
- Known commanded speed
- Measure actual displacement
- Estimate slip vs load

## Step 2 -> Sinkage Estimation
- Measure wheel penetration (sim or physical)
- Fit Bekker parameters kc, kφ, n

## Step 3 -> Traction Curve Fit
- Perform increasing torque tests
- Fit (c, φ, K) to measured traction vs slip

## Step 4 -> Cross-Validation
- Validate on:
  - incline runs
  - obstacle traversal
  - dune scenario

Minimize error:

E = || v_measured - v_model ||²

Use nonlinear least squares or Bayesian parameter estimation.

---

# 11. Simulation Requirements

Simulation must:

- Compute sinkage from wheel load
- Modify effective radius if z significant
- Reduce forward velocity via slip model
- Limit traction when τ saturates

Validation metrics:

- Slip ratio error < 5% in controlled scenario
- Traction prediction within 10% of reference dataset

---

# 12. Limitations

This model:

- Assumes homogeneous soil
- Ignores lateral soil flow
- Does not model wheel cleat effects
- Does not capture soil compaction history

For high-fidelity studies:
- Discrete Element Method (DEM) required

---

# Conclusion

Terramechanics layer converts:

Wheel angular velocity  
-> slip ratio  
-> shear stress  
-> traction force  
-> effective vehicle velocity  

_This is the bridge between kinematics and real Mars mobility._
