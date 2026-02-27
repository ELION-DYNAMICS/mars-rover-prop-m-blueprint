# Expected artifacts: lander_tether_site

A valid run must produce:

## Dataset directory
`datasets/<run_id>/`

## Required files
- `run.mcap`
- `run_metadata.json` (schema-valid)
- `metrics.json` (placeholder acceptable in Phase 0)
- optional: `plots/` (if generated)

## Required metadata fields
- scenario = "lander_tether_site"
- mode ∈ {simulation, hardware}
- backend ∈ {gazebo, webots, pybullet, hardware}
- git commit + dirty state
- recorded topics list
