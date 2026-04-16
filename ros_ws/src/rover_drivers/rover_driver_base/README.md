# rover_driver_base

`rover_driver_base` defines the current driver-layer boundary for the rover workspace.

It is intentionally modest in scope:

- provide simulation bridge nodes that satisfy higher-layer topic contracts
- mark the handoff point between control and actuation
- preserve a stable interface so future hardware drivers can replace simulation nodes without forcing architectural rewrites above them

## Current Scope

The package currently ships four ROS 2 Python nodes:

- `sim_imu_node`
- `sim_encoder_node`
- `sim_contacts_node`
- `sim_motor_interface_node`

These are not full-fidelity sensor models. They are interface-preserving bridge nodes for bringup, integration, and early simulation workflows.

## Boundary Definition

The intended layering is:

- `rover_control` publishes constrained vehicle commands on `/cmd_vel_safe`
- `rover_driver_base` receives those commands and bridges them toward simulation or future hardware interfaces
- higher layers should not need to know whether the downstream path is simulation or physical hardware

This package exists to keep that boundary explicit.

## Current Limitations

- IMU, encoder, and contact outputs are still simplified
- the motor interface is still a topic bridge, not a validated low-level actuator driver
- hardware-specific drivers are not implemented here yet

That is acceptable at the current repository stage, as long as the package is treated as a boundary layer rather than as proof of hardware readiness.
