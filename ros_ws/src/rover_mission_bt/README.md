# rover_mission_bt

Mission-cycle package for rover operational phases.

Primary cycle:
Drive -> Stop/Measure -> Transmit/Log -> Repeat

This package currently provides:
- authored XML trees in `trees/`
- a deterministic runtime node that:
  - loads a selected tree file for traceability
  - advances mission phases at a fixed rate
  - publishes mission state to `/mission/state`

What it does not yet provide:
- a full BehaviorTree.CPP execution runtime
- complex condition/action plugins
- deep recovery-tree semantics

Modes:
- Modern: more continuous driving, shorter measure window
- PROP-M: conservative stop-measure-continue behavior

This layer is mission logic only.
It must not contain control tuning or estimation logic.
