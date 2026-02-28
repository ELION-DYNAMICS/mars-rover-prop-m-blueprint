# Hazard Register: mars_rocks

## H-01: Rock collision
- Description: Rover contacts or climbs rocks, invalidating run and risking hardware.
- Cause: costmap not seeing obstacles, wrong footprint, insufficient inflation, localization drift.
- Mitigation:
  - inflation radius tuned per mode
  - conservative recovery behaviors enabled
  - stop/measure cadence reduces drift accumulation
- Verification:
  - contact sensors (Phase 1)
  - post-run distance-to-obstacle metrics (Phase 1)

## H-02: Planner/controller deadlock
- Description: Nav2 fails to produce progress or oscillates around obstacles.
- Cause: controller parameters too aggressive, goal tolerance too strict, poor costmap source.
- Mitigation:
  - regulated pure pursuit conservative settings
  - recovery behaviors configured (backup/wait)
- Verification:
  - mission phase duration metrics flag stalls

## H-03: False stability in sim
- Description: The sim doesn’t model contact realistically; collisions appear harmless.
- Mitigation:
  - treat any contact as run failure regardless of visual outcome
  - enforce contact detection and gating in metrics (Phase 1)
