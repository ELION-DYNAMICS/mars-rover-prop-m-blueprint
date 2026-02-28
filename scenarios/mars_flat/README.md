# Scenario: Mars Flat

## Purpose

Mars Flat is the baseline control scenario for the rover program.

This environment represents:
- Flat terrain
- Nominal regolith traction
- No geometric obstacles
- No tether constraints
- No dune fields

If the rover stack cannot operate deterministically here,
it has no business being evaluated in complex environments.

This scenario exists to:
- validate basic Nav2 + control wiring
- verify stop/measure mission cadence
- validate dataset packaging and schema
- provide a regression reference

---

## Engineering Role

Mars Flat is:

- the CI smoke-test world
- the calibration baseline
- the reference for performance comparison

All future scenario performance should be measured relative to Mars Flat.

---

## Acceptance Criteria (Phase 0)

A valid run must:

1. Complete ≥ 3 mission cycles.
2. Show no TF discontinuities.
3. Produce no NaN velocities.
4. Maintain stable `/cmd_vel_safe` shaping.
5. Package a dataset that validates against schema.

No performance heroics required.
Stability and reproducibility only.
