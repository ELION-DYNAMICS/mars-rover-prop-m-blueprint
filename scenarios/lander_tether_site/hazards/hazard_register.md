# Hazard Register: lander_tether_site

## H-01: Lander collision
- Description: Rover impacts lander structure causing mission failure or hardware damage.
- Cause: Planner does not respect keep-out region; costmap missing obstacle; localization drift.
- Mitigation:
  - Keep-out zone in global costmap (static obstacle layer or map encoding)
  - Conservative inflation radius near lander
  - Mission BT includes stop/measure cadence near lander
- Verification:
  - Log minimum distance to lander per run (metric required in Phase 1)

## H-02: Tether entanglement (modeled as keep-out corridor)
- Description: Rover crosses tether corridor and becomes immobilized or causes lander upset.
- Cause: Corridor not represented in costmap; operator sends manual /cmd_vel.
- Mitigation:
  - Corridor encoded as lethal cost
  - Control watchdog + speed limits in PROP-M mode
- Verification:
  - Reject runs where path or pose enters corridor polygon

## H-03: Loss of comms / incomplete evidence
- Description: Run cannot be reproduced or audited due to missing data products.
- Cause: Bag not recorded, metadata missing, packaging skipped.
- Mitigation:
  - rover_tools packaging required for valid run
  - schema validation hard-fails
