# Electrical Architecture

This document defines the rover electrical system for both:
- Simulation parity _(signal-level contracts)_
- Hardware implementation _(drivers, interfaces, power constraints)_

The goal is to ensure every “important wire” has a software counterpart:
- command -> actuator
- sensor -> estimation
- diagnostics -> safety

---

## 1) Top-Level Block Diagram

Power Source _(Battery / Supply)_
  -> Power Distribution _(PDU + fuses)_
    -> Motor Power Rail _(high current)_
    -> Logic Power Rail _(regulated 5V/3V3)_
    -> Sensor Power Rail _(low noise, optional)_

Compute
  -> MCU _(real-time motor/sensor IO)_
  -> SBC _(high-level autonomy: ROS 2 + Nav2)_
  -> Comm link _(wired/tether or radio)_

Actuation
  -> Motor Drivers _(H-bridge / ESC)_
  -> Motors _(wheel actuators)_

Sensing
  -> Wheel Encoders
  -> IMU
  -> Contact/Tactile Bars
  -> Optional: Camera / LiDAR

Safety
  -> E-stop
  -> Watchdog
  -> Current/Voltage monitoring
  -> Thermal monitoring

---

## 2) Compute Partitioning 

### 2.1 MCU _(Hard Real-Time)_
Responsibilities:
- wheel velocity/torque control loop _(100–1000 Hz)_
- encoder sampling + timestamping
- IMU polling _(if directly connected)_
- safety interlocks _(E-stop, watchdog)_
- publishes minimal state to SBC

Interfaces:
- CAN or UART/USB to SBC
- PWM/DIR or CAN to motor drivers
- Quadrature encoder inputs
- GPIO for contact sensors
- ADC for current/voltage/temperature

### 2.2 SBC _(High-Level ROS 2)_
Responsibilities:
- mission executive _(BT)_
- navigation stack _(Nav2)_
- state estimation _(EKF fusion)_
- logging _(MCAP)_
- dataset export + metrics

Interfaces:
- ROS 2 network
- bridge to MCU _(micro-ROS, rosserial-like, custom)_
- optional perception sensors _(USB/CSI/Ethernet)_

---

## 3) Power Architecture

### 3.1 Rails
- VBAT: main battery rail _(e.g., 12–24V nominal)_
- VMOTOR: high current motor rail _(often VBAT or regulated)_
- VLOGIC: 5V regulated for compute + logic
- VSENSE: 5V/3V3 low-noise for IMU/analog

### 3.2 Protection _(Non-Negotiable)_
- fuse or polyfuse per motor driver channel
- reverse polarity protection
- undervoltage cutoff _(protect battery + prevent brownouts)_
- inrush limiting for SBC
- common ground strategy documented

### 3.3 Telemetry Requirements
- voltage _(VBAT)_
- current total + per motor channel if possible
- temperatures _(driver + motors if possible)_

Publish to:
- `/diagnostics`
- `/power/*` topics _(software contract)_

---

## 4) Actuation Subsystem

### 4.1 Motor Driver Interface Options
Choose one _(document the chosen option and delete the others later)_:

A) PWM + DIR
- Pros: simple
- Cons: limited telemetry unless additional wiring

B) CAN _(smart driver)_
- Pros: telemetry + robust bus
- Cons: complexity

C) Serial _(UART/RS485)_
- Pros: moderate complexity
- Cons: timing and reliability depends on implementation

### 4.2 Required Signals
Minimum:
- command: target wheel angular velocity OR target torque
- feedback: measured wheel angular velocity
- faults: overcurrent, overtemp, undervoltage, driver error

ROS 2 mapping (contract):
- command in: `/cmd_vel_safe` -> wheel setpoints
- feedback out: `/joint_states`, `/wheel/odometry_raw`
- faults out: `/diagnostics`

---

## 5) Sensing Subsystem

### 5.1 Wheel Encoders
Type:
- Quadrature incremental _(A/B)_ OR absolute encoder

Minimum spec targets:
- resolution: >= 500 counts/rev _(prefer higher)_
- timestamped sampling at >= 200 Hz equivalent

ROS mapping:
- publish joint positions/velocities in `/joint_states`

### 5.2 IMU
Interface:
- SPI preferred _(timing)_, I2C acceptable _(short wires)_

ROS mapping:
- publish `sensor_msgs/Imu` on `/imu/data`

### 5.3 Contact / Tactile Bars _(PROP-M mode)_
Implementation options:
- simple digital switches _(GPIO)_
- force sensors _(analog)_
- bump sensors with debouncing logic

ROS mapping:
- publish `/contacts/left`, `/contacts/right` (custom msg recommended)

---

## 6) Communications (Tether or Modern)

### 6.1 PROP-M Mode (Tether Emphasis)
- tether implies:
  - power possible 
  - comm stability high
  - hard radius constraint enforced in software

### 6.2 Modern Mode
- Wi-Fi / radio link:
  - latency + packet loss must be tolerated
  - logging must be onboard

---

## 7) Timing and Synchronization

- MCU provides monotonic timestamps for encoder + IMU data
- SBC time sync strategy:
  - ROS time in sim
  - steady-clock alignment in hardware
  - optionally sync via time offset estimation

Requirement:
- every sensor message must be timestamped at acquisition time

---

## 8) Safety Architecture

### 8.1 E-stop
- hard cuts motor power OR disables driver enable lines
- SBC must also observe E-stop state and stop commanding

### 8.2 Watchdog
- if SBC command stream stops > T seconds:
  - MCU forces velocity to zero
  - raises fault

### 8.3 Fault States
Define fault classes:
- WARN: degraded, continue
- FAULT: stop motion, require recovery action
- FATAL: hard stop, manual intervention

ROS mapping:
- `/diagnostics`
- `/fault_manager/state` 

---

## 9) Simulation Parity _(Must Match Hardware Contracts)_

Even in SIM, the following must exist as topics/messages:
- `/power/*` telemetry _(simulated)_
- `/diagnostics`
- `/contacts/*`
- `/joint_states`
- `/imu/data`

The point:
If the software runs in SIM but cannot run on HW without rewiring topics, the architecture is wrong.

---

## 10) Open Decisions _(Track as Issues)_

- Motor interface: PWM/DIR or CAN
- Encoder type + resolution target
- Compute: SBC-only or SBC+MCU split
- Power rail nominal voltage and current budget
- Safety implementation details _(watchdog threshold, estop wiring)_
