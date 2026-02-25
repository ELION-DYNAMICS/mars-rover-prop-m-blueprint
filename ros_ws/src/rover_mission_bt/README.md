# rover_mission_bt

Mission Behavior Trees for rover operational cycles.

Primary cycle:
Drive -> Stop/Measure -> Transmit/Log -> Repeat

This package provides:
- BT XML definitions in `trees/`
- A minimal runtime node that:
  - loads a BT file
  - ticks at a fixed rate
  - publishes mission state to `/mission/state`

Modes:
- Modern: more continuous driving, shorter measure window
- PROP-M: conservative "stop-measure-continue" behavior

This layer is mission logic only.
It must not contain control tuning or estimation logic.
