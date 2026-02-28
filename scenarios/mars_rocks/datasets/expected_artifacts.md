# Expected artifacts: mars_rocks

Required:
- run.mcap
- run_metadata.json (schema-valid)
- metrics.json (placeholder acceptable in Phase 0)

Metadata must include:
- scenario = "mars_rocks"
- rock_field_version = "RF-001"
- mode/backend recorded
- git commit + dirty state
- recorded topics list non-empty

Phase 1 adds:
- collision/contact metric
- minimum clearance proxy
