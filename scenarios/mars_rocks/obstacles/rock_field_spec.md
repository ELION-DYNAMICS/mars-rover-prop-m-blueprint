# Rock Field Spec: RF-001

## Purpose
Create a static corridor that forces non-trivial planning while remaining reproducible.

## Layout
- Two boundary lines of rocks form a corridor ~3 m wide.
- Two mid-field rocks create a planning decision (left/right bias).
- Rocks are static and placed deterministically.

## Constraints
- Rock radii: 0.18-0.24 m
- Minimum corridor clearance must exceed rover radius + inflation.

## Phase 1
- Replace spheres with mesh rocks for more realistic collision geometry.
- Add a "rock density" parameter and deterministic generator tied to seed.
- Add automated collision checks (contact sensor topics + metrics gate).
