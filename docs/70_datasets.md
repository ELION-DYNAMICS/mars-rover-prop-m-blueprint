# Dataset Management and Governance

This document defines how simulation and experimental data
are generated, stored, versioned, and evaluated.

Data is treated as a first-class engineering artifact.

Every simulation run produces:

-> Raw telemetry (MCAP)
-> Structured metadata
-> Computed metrics
-> Version references

No undocumented runs are accepted.

---

# 1. Dataset Objectives

Datasets exist to:

- Validate models
- Tune estimation
- Calibrate terramechanics
- Compare algorithm revisions
- Enable regression testing
- Support reproducible research

If a dataset cannot be reproduced,
it is not considered valid.

---

# 2. Dataset Structure

Each run must produce:

datasets/
    <run_id>/
        run_metadata.json
        run.mcap
        metrics.json
        environment.yaml
        model_params.yaml
        README.md

Run ID format:

YYYYMMDD_HHMMSS_<scenario>_<git_short_hash>

Example:

20260218_153012_mars_flat_a83f2c1

---

# 3. Metadata Specification

## 3.1 run_metadata.json

Must include:

- Run ID
- Git commit hash
- Scenario name
- Random seed
- Simulation backend (gazebo / webots / pybullet)
- Physics step size
- Control frequency
- Estimator configuration
- Terramechanics parameters
- Date/time
- Operator (if hardware)

This ensures full traceability.

---

# 4. Metrics Specification

## 4.1 metrics.json

Must include:

- Total distance traveled
- Final pose error
- Average slip ratio
- Maximum slip ratio
- Number of recovery events
- Maximum distance from lander
- Mission duration
- Energy proxy (if computed)

Metrics must be deterministic for identical seeds.

Threshold values defined in V&V document.

---

# 5. Raw Data (MCAP)

MCAP file must contain:

- /tf
- /joint_states
- /cmd_vel
- /odometry/filtered
- /imu/data
- /wheel/slip_estimate
- /mission/state
- /diagnostics

Ground truth (simulation only):

- /ground_truth/pose

Ground truth is used only for evaluation,
never fed into estimator.

---

# 6. Parameter Archiving

Each run must store:

environment.yaml
model_params.yaml

These include:

- Wheel radius
- Wheel separation
- Mass
- kc, kφ, n
- c, φ, K
- Controller gains
- Estimator Q and R

No parameter must be implied.

All parameters must be explicit.

---

# 7. Versioning Policy

Datasets are immutable.

If a dataset changes:

-> New run ID
-> New directory

Never overwrite existing datasets.

Large datasets may be:

- Stored via Git LFS
- Archived externally
- Indexed with manifest file

---

# 8. Dataset Categories

Datasets are categorized as:

- baseline
- calibration
- regression
- stress_test
- validation
- hardware (future)

Each run_metadata.json must specify category.

---

# 9. Calibration Datasets

Calibration datasets must:

- Be collected under controlled conditions
- Use known trajectories or loads
- Be documented in README.md

Used for:

- Terramechanics parameter fitting
- Estimator tuning
- Control gain optimization

Calibration must never use regression datasets.

---

# 10. Regression Datasets

Regression datasets:

- Must use fixed random seed
- Must be reproducible
- Must have locked parameters

Any deviation from baseline metrics must trigger review.

Regression runs are part of CI.

---

# 11. Data Integrity

After each run:

- Validate schema
- Verify file completeness
- Compute hash of MCAP file
- Store hash in metadata

Corrupted runs must be rejected.

---

# 12. Statistical Evaluation

Performance comparisons must use:

Mean error  
Standard deviation  
Worst-case deviation  

Single-run improvements are not accepted.

Improvements must be statistically significant across runs.

---

# 13. Reproducibility Requirements

A dataset is reproducible if:

Using:

- Same git commit
- Same seed
- Same parameters
- Same simulator version

Produces:

Metrics within defined tolerance.

Tolerance defined in V&V document.

---

# 14. Storage and Scaling

For large dataset volumes:

Maintain:

datasets_index.json

Containing:

- Run ID
- Scenario
- Date
- Key metrics
- Commit hash

Allows fast querying without loading raw data.

---

# 15. Engineering Discipline

Evidence must be:

- Structured
- Traceable
- Reproducible
- Immutable

Visual inspection is insufficient.

Only quantified metrics determine progress.

If results cannot be reproduced,
the result does not exist.
