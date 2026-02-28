# Expected artifacts: mars_dunes

A valid run must produce:

## Dataset directory
`datasets/<run_id>/`

## Required files
- `run.mcap`
- `run_metadata.json` (schema-valid)
- `metrics.json` (placeholder acceptable in Phase 0)

## Required metadata fields
- scenario = "mars_dunes"
- terrain preset used (regolith_loose)
- seed recorded (even if unused today)
- mode/backend recorded
- recorded topic list non-empty
