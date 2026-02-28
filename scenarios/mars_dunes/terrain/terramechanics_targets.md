# Terramechanics Targets (Mars Dunes)

This document defines what we intend to measure in this scenario.

## Primary signals
- slip ratio estimate (per wheel and aggregate)
- commanded vs achieved velocity (progress efficiency)
- stop/measure dwell stability (pose drift while stopped)
- controller saturation events (rate limiting / slip containment activation)

## Phase 0 qualitative targets
- system remains stable under low traction
- command shaping prevents runaway behavior when progress collapses
- dataset contains enough signals to compute slip proxies offline

## Phase 1 quantitative targets (to be defined)
- mean slip ratio threshold by segment
- maximum sustained slip duration
- minimum progress per unit commanded distance
