# Hazard Register: mars_dunes

## H-01: Mobility loss / immobilization
- Description: Rover fails to make forward progress due to low traction.
- Cause: high slip, insufficient normal load distribution, poor controller tuning.
- Mitigation:
  - conservative velocity in PROP-M mode
  - command shaping watchdog + accel limiting
  - mission cadence includes stop/measure for stability assessment
- Verification:
  - metrics must report progress efficiency (Phase 1)

## H-02: Controller instability in low traction
- Description: Oscillation or runaway commands due to poor coupling between planner/controller and ground truth.
- Cause: aggressive controller parameters, unrealistic sim contacts, missing rate limiting.
- Mitigation:
  - regulated pure pursuit conservative defaults
  - strict acceleration limiting in rover_control
- Verification:
  - reject runs with NaNs, TF discontinuities, or unbounded velocities

## H-03: False confidence from visuals
- Description: Video looks plausible; physics is wrong; calibration becomes meaningless.
- Cause: untracked parameter drift and ad-hoc simulator tuning.
- Mitigation:
  - terrain preset is explicit and logged
  - dataset packaging + schema validation required
  - acceptance criteria centered on data, not rendering
