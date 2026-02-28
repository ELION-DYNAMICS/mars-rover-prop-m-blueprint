# Dune Field Specification (Phase 0)

## Intent
A repeatable "dune-like" mobility stress environment for:
- slip characterization
- controller stability testing
- terramechanics calibration dataset generation

## Current implementation
- Terrain geometry: flat plane placeholder (`regolith_dune_patch` model)
- Terrain behavior: friction preset `regolith_loose` applied via world plugin

This is a deliberate Phase 0 simplification:
we lock down the data pipeline before introducing complex heightmaps.

## Phase 1 upgrade
- Replace plane with heightmap-based dune field
- Record heightmap asset hash and generation seed in run metadata
- Add localized steep slopes (10-20 deg) and troughs for sinkage events
