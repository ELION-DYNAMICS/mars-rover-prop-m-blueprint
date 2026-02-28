# Hazard Register: mars_flat

## H-01: False confidence
- Description: Flat terrain masks integration errors.
- Mitigation:
  - Must pass before moving to dunes or tether scenarios.
  - Metrics must still be generated.

## H-02: Silent command shaping failure
- Description: /cmd_vel_safe not properly limiting commands.
- Mitigation:
  - Explicit logging of shaped vs commanded velocity.
  - Reject runs with unbounded accelerations.

## H-03: Missing dataset packaging
- Description: “We ran it” without evidence.
- Mitigation:
  - No run is valid without packaging under /datasets.
