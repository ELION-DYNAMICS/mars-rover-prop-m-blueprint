# rover_tools

Operational tooling for the rover program.

Functions:
- bag recording (rosbag2) with approved topic sets
- bag export (MCAP->CSV) for offline analysis when needed
- dataset packaging: creates datasets/<run_id>/ with run_metadata.json + checksums
- schema validation: validates run_metadata.json against datasets/schemas/run_metadata.schema.json
- metrics evaluation scaffold: generates metrics.json from a run and spec

Policy:
- datasets are immutable once written
- schema validation is mandatory
- all outputs must be deterministic and traceable (commit, configs, seed)