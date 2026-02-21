# State Estimation

This document defines the rover state estimation architecture.

The estimator provides:

- Pose (X, Y, θ)
- Linear and angular velocity
- Covariance (uncertainty)
- Slip-aware correction capability

It does NOT command actuators.
It does NOT perform planning.
It produces the best physically consistent estimate of the rover state.

---

# 1. Estimation Objectives

The estimator must:

- Fuse wheel odometry and IMU data
- Provide drift-bounded pose in local frame
- Maintain covariance consistency
- Remain stable under slip
- Operate in real time

Two operational modes:

1. Minimal Mode (PROP-M emulation)
2. Modern Mode (optional SLAM integration)

---

# 2. State Definition

State vector:

x = [ X, Y, θ, v, ω ]ᵀ

Where:

X, Y  -> position in `odom` frame  
θ     -> heading  
v     -> forward velocity  
ω     -> yaw rate  

Covariance matrix:

P ∈ R⁵ˣ⁵

---

# 3. Process Model

Propagation uses differential drive kinematics:

Ẋ = v cos(θ)  
Ẏ = v sin(θ)  
θ̇ = ω  
v̇ = a_process  
ω̇ = α_process  

Process noise accounts for:

- Slip
- Terrain variation
- Encoder quantization
- Model simplification

Discrete-time update:

xₖ₊₁ = f(xₖ, uₖ) + wₖ

wₖ ~ N(0, Q)

---

# 4. Sensor Inputs

## 4.1 Wheel Odometry

Provides:

- Wheel angular velocity
- Derived linear velocity

Limitations:

- Overestimates displacement under slip
- Biased on deformable terrain

---

## 4.2 IMU

Provides:

- Angular velocity (gyro)
- Linear acceleration

Advantages:

- Independent yaw rate measurement
- Useful during slip

Limitations:

- Bias drift
- Noise
- Mars-representative low dynamics

---

## 4.3 Optional Sensors (Modern Mode)

- Visual odometry
- LiDAR scan matching
- Absolute positioning (sim ground truth only for evaluation)

---

# 5. Estimator Type

Recommended baseline:

Extended Kalman Filter (EKF)

Justification:

- Nonlinear system
- Computationally efficient
- Well-understood failure modes
- Suitable for low-speed rover

Alternative (future):

- UKF
- Factor graph / graph-SLAM

---

# 6. Measurement Model

Measurement vector:

z = [ v_wheel, ω_imu ]ᵀ

Measurement equations:

v_meas = v + noise_v  
ω_meas = ω + noise_ω  

Measurement update:

zₖ = h(xₖ) + vₖ  
vₖ ~ N(0, R)

---

# 7. Slip Handling

Slip causes:

v_wheel > v_actual

Strategy:

Increase process noise Q when slip ratio increases.

If:

s > s_threshold

Then:

Q_v -> Q_v * β

Where:

β > 1

This allows filter to trust IMU more than wheel odometry.

Slip-aware covariance inflation prevents filter divergence.

---

# 8. Covariance Management

Covariance must:

- Grow under uncertainty
- Decrease under strong measurements
- Never collapse unrealistically

Monitoring:

trace(P) must remain bounded  
Negative eigenvalues forbidden  

Filter must reject outlier measurements using innovation gating:

If:

|innovation| > kσ

Reject measurement.

---

# 9. Frame Relationships

ROS frames:

map -> global reference  
odom -> locally consistent frame  
base_link -> rover body  

Estimator publishes:

`odom -> base_link` transform

In Modern Mode:

SLAM provides:

`map -> odom` correction

PROP-M Mode:

`map` may be omitted  
Operate purely in `odom`

---

# 10. Initialization

Initialization must set:

X = 0  
Y = 0  
θ = 0  
P initialized with realistic uncertainty

Do NOT initialize covariance to near-zero.

Initial uncertainty should reflect:

- Unknown orientation bias
- Wheel encoder noise

---

# 11. Failure Modes

Estimator must detect:

- IMU dropout
- Encoder freeze
- Unbounded covariance growth
- Innovation divergence

On failure:

- Publish diagnostic state
- Increase covariance
- Signal fault manager

Never silently reset state.

---

# 12. Simulation vs Hardware

## Simulation

- Ideal timing
- Deterministic noise injection
- Ground truth available for validation only

Estimator must not access ground truth directly.

## Hardware

- Timing jitter
- Bias drift
- Temperature effects
- Encoder quantization

Filter must tolerate:

- Variable dt
- Measurement latency

---

# 13. Performance Metrics

mars_flat:

- Position drift < 1% over 10 m
- Heading drift < 2°

mars_dunes:

- No divergence
- Covariance consistent with observed error

landed tether site:

- Maintain position within 0.5 m over cyclic stops

---

# 14. Engineering Discipline

Estimation is not tuned until it “looks good.”

It is tuned against:

- Logged datasets
- Known trajectories
- Reproducible regression scenarios

Every change to Q or R must be justified.

No hidden constants.

All parameters versioned.
