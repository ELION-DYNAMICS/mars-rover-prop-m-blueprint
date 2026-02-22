# Nav2 Profiles

This directory contains Navigation2 (Nav2) configuration profiles.

Profiles are separated by mission mode.

They define:

- Controller behavior
- Planner behavior
- Costmap parameters
- Velocity limits
- Recovery policies

Profiles must remain consistent with:

- control_defaults.yaml
- estimator_defaults.yaml
- terramechanics_defaults.yaml

No profile may violate physical limits defined in control configs.

---

## Available Profiles

rover_v1.yaml  
Modern baseline navigation profile.

rover_prop_m_mode.yaml  
PROP-M style constrained mode:
- Low speed
- Conservative planning
- Stop-measure-continue behavior
