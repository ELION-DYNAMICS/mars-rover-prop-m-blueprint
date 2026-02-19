# Mechanical Architecture

This document defines the physical structure of the Mars Rover Prop-M Blueprint platform.

Scope:
- Structural layout
- Mobility system
- Load paths
- Mechanical interfaces
- Environmental constraints
- Design assumptions

This architecture supports:
- PROP-M Mode _(tether-limited science rover)_
- Modern Autonomous Mode

---

# 1. System Overview

The rover is a compact, low-speed, high-stability planetary exploration platform designed for:

- Low gravity environments _(Mars: 3.71 m/s²)_
- Loose regolith terrain
- Low-speed precision mobility
- High reliability over efficiency

Primary design priorities:
1. Stability over speed
2. Simplicity over complexity
3. Robustness over mass optimization

---

# 2. Structural Layout

## 2.1 Chassis

Type:
- Rigid central body
- Rectangular or trapezoidal base frame

Material assumptions:
- Aluminum alloy _(6061-T6 equivalent)_
- Alternative: carbon composite _(future revision)_

Key properties:
- Low center of mass
- Symmetric mass distribution
- Mounting rails for modular payload

Chassis functions:
- Load-bearing structure
- Electronics enclosure
- Motor mount support
- Tether anchor interface

---

## 2.2 Dimensions _(Initial Reference Model)_

Example baseline values:

Length: 0.6 m  
Width: 0.45 m  
Height: 0.25 m  
Wheel diameter: 0.18-0.22 m  
Track width (L): 0.35-0.40 m  

These values must match kinematic model parameters.

---

# 3. Mobility System

## 3.1 Configuration

Differential drive:
- 2 driven wheels _(left, right)_
- Optional passive caster _(rear or front)_
- Or 4-wheel skid steer _(future variant)_

PROP-M reference:
- Low-speed incremental motion
- High torque at wheels

---

## 3.2 Wheels

Design goals:
- High traction on loose soil
- Low sinkage
- Minimal clogging

Assumed characteristics:
- Rigid wheel with grousers
- Width ≥ 0.05 m
- Diameter chosen for torque efficiency

Parameters:
- Wheel radius r _(defined in kinematics.md)_
- Wheel inertia J_w _(defined in dynamics.md)_

---

## 3.3 Drive System

Motor type:
- Brushless DC motor _(modern mode)_
- Geared DC motor _(simplified)_

Transmission:
- Planetary gearbox
- Gear ratio: 20:1 - 50:1 typical

Requirements:
- High torque at low speed
- Backlash minimized
- Encoder integration

Mounting:
- Direct axle mount or supported via bearing housing

---

# 4. Load Paths

Primary load transfer:

Ground -> Wheel -> Axle -> Bearing -> Motor Mount -> Chassis

Design must ensure:
- Axial load capacity
- Bending resistance
- Shock absorption

Static load per wheel:

F_w ≈ (m_total * g_mars) / number_of_support_points

Example:
m = 20 kg  
g_mars = 3.71 m/s²  

Total weight ≈ 74 N  
Per wheel (2 driven) ≈ 37 N  

Dynamic loads must include:
- Obstacle climb forces
- Shock multiplier (~2-3x static)

---

# 5. Tether Interface _(PROP-M Mode)_

Constraints:
- Maximum radius: 15 m
- Rear-mounted tether anchor

Mechanical considerations:
- Reinforced anchor bracket
- Tether strain relief
- Avoid wheel entanglement

Load case:
- Tether tension under drag
- Peak transient load during boundary enforcement

Anchor must tolerate:
≥ 2x maximum expected tether tension

---

# 6. Payload Mounting System

Science module location:
- Center-top or forward-mounted

Mount requirements:
- Vibration isolation
- Modular attachment interface
- Defined center-of-mass offset

Measurement probe interface:
- Downward actuation port
- Fixed or deployable arm

---

# 7. Environmental Design Constraints

## 7.1 Temperature

- −120°C to +20°C equivalent _(Mars simulation domain)_
- Materials must tolerate thermal cycling

## 7.2 Dust

- Sealed bearings
- Motor protection
- Cable routing internal

## 7.3 Gravity Effects

Lower gravity implies:
- Reduced normal force
- Higher slip probability
- Stability influenced more by geometry than mass

---

# 8. Stability Considerations

## 8.1 Static Stability

Center of mass _(CoM)_ must satisfy:

Projection of CoM ∈ support polygon

Max slope angle:

θ_max ≈ arctan( (half track width) / CoM height )

Design target:
- ≥ 20° static slope tolerance

---

## 8.2 Tip-Over Margin

Factors:
- Sudden obstacle contact
- Tether pull force
- Rapid yaw rotation

Mitigation:
- Low CoM
- Wide track
- Speed limiting in control layer

---

# 9. Mass Budget (Initial Estimate)

Chassis: 6 kg  
Motors + drivetrain: 4 kg  
Wheels: 2 kg  
Electronics: 3 kg  
Battery: 3 kg  
Payload: 2 kg  

Total ≈ 20 kg baseline

Mass budget must align with:
- Torque requirements _(dynamics.md)_
- Sinkage model _(terramechanics.md)_

---

# 10. Interfaces to Other Systems

Mechanical architecture interfaces with:

- Kinematics model _(wheel radius, track width)_
- Dynamics model _(mass, inertia tensor)_
- Control system _(torque limits, speed limits)_
- Simulation _(URDF inertial + collision models)_

All physical parameters must be:

Defined once -> Referenced consistently across stack.

---

# 11. Simulation Mapping

URDF must include:

- Accurate inertial tensors
- Collision geometry
- Visual geometry
- Joint limits
- Transmission definitions

No placeholder inertias allowed in final validation builds.

---

# 12. Revision Strategy

Mechanical architecture evolves in phases:

Phase 1:
- Simple rigid differential drive

Phase 2:
- Improved wheel geometry
- Suspension option

Phase 3:
- Advanced terrain compliance

Each revision must preserve:
- Kinematic compatibility
- Topic contract stability
- Control interface consistency

