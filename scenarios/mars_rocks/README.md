# Scenario: Mars Rocks

## Purpose
Mars Rocks is the obstacle-field scenario for validating:

- costmap obstacle handling (local + global)
- planner/controller behavior around discontinuous hazards
- recovery behaviors under blockage
- disciplined dataset production (not “looks good in RViz”)

This scenario is specifically designed to catch failures that flat terrain will never reveal:
bad costmap sources, insufficient inflation, incorrect footprint/robot radius, and brittle controllers.

---

## Engineering Objectives
1. Demonstrate safe navigation through a defined rock corridor without collisions.
2. Validate recovery actions trigger and resolve common blockages (backup, wait, spin if enabled).
3. Produce datasets that allow offline analysis of:
   - path efficiency
   - stop/measure phase stability near obstacles
   - minimum obstacle clearance proxy

---

## Acceptance Criteria (Phase 0)
A run is valid if:
- Rover completes ≥ 3 mission cycles without contacting rocks (collision-free by inspection + future contact sensors).
- Nav2 remains stable (no TF discontinuities, no NaNs).
- Dataset packages successfully and validates schema.
- Metadata explicitly records scenario `mars_rocks`, rock field version, and seed.

Phase 1 introduces quantitative clearance and collision checks.

---

## Notes
Rocks are hazards, not decoration.
If you can’t explain why a rock is placed, it doesn’t belong in this scenario.
