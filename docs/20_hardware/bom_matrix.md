# Bill of Materials _(BOM)_ Matrix

This matrix defines the minimum hardware reference design for:
- Simulation parameter grounding _(mass/inertia, wheel geometry, motor limits)_
- Future hardware build 
- Clear interface boundaries for drivers

Parts are specified by performance envelope.

---

## 1) Rover Variant Definitions

| Variant | Purpose | Notes |
|---|---|---|
| SIM-REF | Simulation reference rover | Must define geometry + inertias + actuator limits |
| HW-REF | Hardware reference rover | Optional build; matches SIM-REF as closely as possible |
| PROP-M | Tether-limited minimal sensor rover | Emphasis on tactile + odometry |

---

## 2) System BOM Matrix _(Top Level)_

| Subsystem | Item | Spec _(Envelope)_ | Qty | Variant | Notes |
|---|---|---:|---:|---|---|
| Chassis | Frame + mounts | lightweight, rigid | 1 | SIM-REF/HW-REF | material: Al/CF optional |
| Mobility | Wheels | radius r, width w | 2+ | all | define r precisely _(model parameter)_ |
| Mobility | Wheel hubs/bearings | radial load rated | 2+ | HW-REF | sim uses ideal joint |
| Actuation | DC/BLDC motors | torque τ_cont, τ_peak | 2+ | all | define torque-speed curve |
| Actuation | Motor drivers | current limit I_max | 2+ | HW-REF | supports velocity mode |
| Sensing | Wheel encoders | CPR, update rate | 2+ | all | sim publishes joint states |
| Sensing | IMU | 6/9-axis, rate ≥100 Hz | 1 | all | noise model required in SIM |
| Sensing | Contact/tactile bars | binary/analog contact | 2 | PROP-M | left/right contact required |
| Compute | Onboard CPU | ROS 2 capable | 1 | HW-REF | x86/ARM; deterministic clock |
| Comms | Telemetry link | sim-only or real | 1 | all | in sim: topic-based |
| Power | Battery / supply | V_nom, peak power | 1 | HW-REF | defines actuator limits |
| Safety | E-stop / watchdog | hardware cutoff | 1 | HW-REF | mandatory if HW exists |
| Tether | Tether interface | length 15 m | 1 | PROP-M | constraint model required |

---

## 3) Parameter Table _(Must Be Filled)_

These values are mandatory because they drive the models.

| Parameter | Symbol | Unit | Value | Source |
|---|---:|---:|---:|---|
| Wheel radius | r | m | TBD | CAD / measurement |
| Track width | L | m | TBD | CAD / measurement |
| Rover mass | m | kg | TBD | CAD / estimate |
| Yaw inertia | I_z | kg·m² | TBD | CAD / estimate |
| Max linear speed | v_max | m/s | TBD | design |
| Max yaw rate | ω_max | rad/s | TBD | design |
| Motor continuous torque | τ_cont | N·m | TBD | datasheet |
| Motor peak torque | τ_peak | N·m | TBD | datasheet |
| Driver current limit | I_max | A | TBD | datasheet |

---

## 4) BOM Governance

- Every BOM row must map to:
  - a driver node _(hardware)_ OR a simulated publisher _(simulation)_
- Every physical spec must map to:
  - a parameter file in `configs/`
- No “nice-to-have” parts enter the BOM until v0.3.


