# Scenario: Mars Dunes

## Purpose
This scenario is designed to stress rover mobility and navigation in **low-cohesion, high-slip terrain**. The focus is terramechanics-driven: traction, sinkage, slip ratio, and controller stability when the ground is not cooperative.

This is not an “obstacle avoidance” demo. It is a mobility characterization test article.

---

## Engineering Objectives
1. Quantify slip and progress under dune-like terrain presets.
2. Validate conservative command shaping under mobility loss (via `/cmd_vel_safe`).
3. Generate calibration-grade datasets usable by `analysis/calibration` workflows.
4. Provide repeatable regression conditions (fixed world, fixed initial pose, fixed mission cadence).

---

## Acceptance Criteria (Phase 0)
A run is considered valid if:
- Rover completes ≥ 3 mission cycles without numerical instability or NaN states.
- The rover remains controllable (no runaway velocity, no diverging TF).
- Dataset packages successfully and validates schema.
- Metadata records scenario `mars_dunes`, preset, mode, backend, and seed.

Phase 1 will add quantitative thresholds (mean slip, sinkage bounds, energy proxies).

---

## Key Constraints
- Terrain uncertainty is the feature, not a bug.
- The scenario must be reproducible; dunes are not allowed to “randomize themselves” without recording the seed.
- Safety: mission BT must support stop/measure cadence and bounded retry logic.

---

## Artifacts
- `scenario.yaml`: scenario truth file (preset, waypoints, defaults)
- `worlds/gazebo/mars_dunes.sdf`: simulation world definition
- `terrain/`: dune field and terramechanics target specs
- `datasets/expected_artifacts.md`: required evidence per run
- `hazards/hazard_register.md`: hazard log and mitigations
