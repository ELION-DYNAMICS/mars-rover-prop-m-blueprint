# Scenario: Lander Tether Site

## Purpose
This scenario represents a rover operating in the immediate vicinity of a stationary lander where a **tether / cable constraint** is present and must be treated as a safety-critical hazard.

The engineering objective is to validate:
- conservative navigation near obstacles and keep-out zones
- disciplined stop/measure cadence for situational awareness
- consistent dataset packaging and run traceability
- (future) tether-aware planning constraints

This scenario is intended for simulation-first execution with clear migration to hardware test stands.

---

## Operating Assumptions
- Terrain is locally navigable regolith with a defined keep-out boundary around the lander.
- The tether is modeled initially as a keep-out corridor (2D). A physical cable model is out of scope for Phase 0.
- The rover uses `map / odom / base_link` with SI units only.
- Mission cycle is: **Drive -> Stop/Measure -> Transmit/Log -> Repeat**.

---

## Scenario Definition
### Frames
- `map` origin: defined by `map/map.yaml`
- lander reference frame (conceptual): `lander_frame` (not yet implemented in TF)

### Key Areas (2D)
- **Keep-out zone**: circular exclusion region centered on lander
- **Tether corridor**: exclusion polygon approximating tether sweep
- **Science waypoint(s)**: points of interest for Stop/Measure

---

## Acceptance Criteria (Phase 0)
A run is considered valid if:
1. Nav2 produces paths that respect the keep-out zone (via costmap footprint/obstacles).
2. The rover completes at least **3 mission cycles** without entering keep-out regions.
3. A dataset is packaged under `/datasets/<run_id>/` and validates schema.
4. Run metadata explicitly records scenario name `lander_tether_site` and mode/backend.

---

## Artifacts
- `scenario.yaml`: authoritative parameters (zones, waypoints, defaults)
- `worlds/gazebo/lander_tether_site.sdf`: simulation world definition
- `map/`: static map used by Nav2 global costmap
- `missions/`: mode-specific mission parameters for BT runner
- `hazards/hazard_register.md`: hazard log and mitigations
- `datasets/expected_artifacts.md`: required outputs per run

---

## How to Run (Simulation)
This scenario assumes:
- `rover_sim_gazebo` provides the simulator harness
- `rover_navigation` provides Nav2 profiles
- `rover_mission_bt` runs the mission loop
- `rover_tools` records and packages evidence

Typical procedure:
1. Launch world `lander_tether_site.sdf`
2. Launch Nav2 with scenario map + profile (modern or prop_m)
3. Start mission cycle with scenario mission config
4. Record minimal bag topic set
5. Package dataset and validate schema
