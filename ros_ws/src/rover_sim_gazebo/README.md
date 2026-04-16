# rover_sim_gazebo

Gazebo simulation package for Mars Rover Prop-M Blueprint.

Design intent:
- deterministic worlds for calibration and regression
- explicit sensor configuration per mode (modern or prop_m)
- terrain presets controlled via a world plugin (no manual slider tuning)

Contents:
- `worlds/` SDF worlds
- `models/terrain/` reusable terrain tiles (heightmap + material)
- `config/terrain_presets.yaml` friction / compliance presets
- `config/sensors_*.yaml` sensor enablement and noise profiles
- `plugins/` Gazebo world plugin to apply terrain presets

Policy:
- Simulation settings must be reproducible.
- A world must declare: time step, real_time_factor, gravity, lighting.
- Terrain parameters must be tied to a named preset and documented.

This package is used by:
- rover_bringup (sim mode)
- calibration experiments (E01–E04)
- dedicated simulation workflows and local regression runs
