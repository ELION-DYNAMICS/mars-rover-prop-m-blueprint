# Low-Level Control

This document defines the lowest closed-loop control layer of the rover.

This layer is responsible for:

- Tracking commanded wheel velocities
- Enforcing safety limits
- Managing torque output
- Handling slip-aware corrections
- Providing deterministic actuator behavior

It does NOT perform planning.
It does NOT decide mission logic.
It executes commands safely.

---

# 1. Control Layer Responsibilities

The low-level control layer sits between:

Navigation / Mission Layer  
-> Rover Control (Safety Arbitration)  
-> Low-Level Controller  
-> Motor Drivers / Simulation  

It guarantees:

- No direct autonomy access to actuators
- Deterministic response
- Bounded acceleration and torque
- Protection against slip runaway

---

# 2. Control Architecture

## 2.1 Command Flow

Incoming:
`/cmd_vel_safe` (geometry_msgs/Twist)

Converted to:
Desired wheel angular velocities:

ω_r_des  
ω_l_des  

Using inverse kinematics:

ω_r = (1 / r) (v + (L/2) ω)  
ω_l = (1 / r) (v - (L/2) ω)

These values are passed to individual wheel controllers.

---

# 3. Wheel Velocity Control

Each wheel uses an independent closed-loop controller.

## 3.1 Control Objective

Track:

ω_desired -> ω_measured

Minimize:

e(t) = ω_desired - ω_measured

---

## 3.2 PID Controller (Baseline)

Torque command:

τ = Kp e + Ki ∫e dt + Kd de/dt

Where:

τ -> motor torque command  
e -> angular velocity error  

Typical design:

- High Kp for responsiveness
- Small Ki to remove steady-state error
- Minimal Kd (noise sensitive)

---

## 3.3 Anti-Windup

Integrator clamping required when:

|τ| >= τ_max

Prevent integral windup under:

- High load
- Slip
- Obstacle stall

---

# 4. Torque Saturation

Motor torque must obey:

|τ| ≤ τ_max  
|dτ/dt| ≤ τ_rate_limit  

Rate limiting prevents:

- Mechanical shock
- Power spikes
- Simulation instability

---

# 5. Slip-Aware Torque Limiting

If slip ratio s exceeds threshold:

s > s_threshold

Then:

τ_command -> τ_command * α

Where:

0 < α < 1

This prevents uncontrolled wheel spin.

Slip-aware loop:

measure ω  
estimate v_actual  
compute s  
reduce torque if necessary  

This loop operates at high frequency (≥ 100 Hz).

---

# 6. Contact Detection Handling (PROP-M Mode)

If contact sensor triggered:

- Immediately override velocity commands
- Set ω_desired = 0
- Apply controlled reverse maneuver
- Hand control back to mission layer

This override must bypass Nav2.

Safety always wins.

---

# 7. Acceleration Limiting

Linear acceleration constraint:

|dv/dt| ≤ a_max

Angular acceleration constraint:

|dω/dt| ≤ α_max

Implemented via command ramping:

v_cmd(t+1) = v_cmd(t) + clamp(v_target - v_cmd, ±a_max Δt)

Prevents:

- EKF divergence
- Slip spikes
- Power surges

---

# 8. Watchdog and Fault Handling

If no command received within timeout:

t > t_timeout

Then:

- Set ω_desired = 0
- Publish fault state

If encoder feedback invalid:

- Enter degraded mode
- Reduce maximum speed
- Notify fault manager

---

# 9. Simulation vs Hardware Differences

## In Simulation

- Torque applied via physics engine
- No electrical noise
- Deterministic timing
- Slip computed from terramechanics model

## In Hardware

- PWM or current control to motor driver
- Encoder quantization
- Real current sensing
- Latency and jitter must be tolerated

Hardware control loop must run:

≥ 200 Hz preferred

---

# 10. Real-Time Requirements

Low-level loop frequency:

100–500 Hz typical

Must guarantee:

- Fixed update period
- Bounded computation time
- No blocking operations

All logging must be non-blocking.

---

# 11. State Feedback Outputs

Controller publishes:

- `/wheel/velocity_error`
- `/wheel/torque_command`
- `/wheel/slip_estimate`
- `/diagnostics`

These are used by:

- Dataset logging
- Performance metrics
- Fault detection

---

# 12. Stability Considerations

Controller must remain stable under:

- High slip
- Variable load (sinkage changes)
- Small terrain discontinuities
- Battery voltage drop (hardware)

Gain tuning must be validated in:

- Flat scenario
- Rock scenario
- Dune scenario

---

# 13. Acceptance Criteria

Straight line tracking:

Velocity error < 5%

Rotation in place:

Heading error < 3°

Slip containment:

Slip ratio remains < 0.3 under nominal terrain

No oscillatory torque behavior

---

# Conclusion

Low-level control transforms:

Velocity command  
-> Wheel angular velocity  
-> Motor torque  
-> Controlled traction  

It ensures:

Autonomy can think freely  
but physics stays disciplined.
