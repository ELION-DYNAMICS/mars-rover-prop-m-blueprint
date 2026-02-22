# Analysis Framework

The `analysis/` directory contains the formal engineering analysis
environment for the Mars Rover Prop-M Blueprint.

This environment is used to:

- Identify physical model parameters
- Calibrate terramechanics behavior
- Tune estimation noise models
- Validate control stability margins
- Quantify mission performance
- Evaluate regression drift over time

Analysis is not exploratory scripting.

Analysis produces engineering artifacts that directly inform
runtime configuration and system validation.

---

# 1. Purpose

The purpose of this directory is to transform raw datasets into:

-> Verified model parameters  
-> Quantified uncertainty bounds  
-> Performance metrics  
-> Version-controlled configuration updates  

All analysis must be reproducible, traceable, and deterministic.

If a result cannot be reproduced from a dataset and a commit hash,
it is not considered valid.

---

# 2. Separation of Concerns

The repository enforces strict separation between:

Runtime System:
- `ros_ws/`
- `configs/`
- `docs/`
- `scenarios/`

Operational Data:
- `datasets/`

Offline Analysis:
- `analysis/`

The analysis layer must never modify runtime code directly.
It may only generate configuration artifacts that are explicitly reviewed and merged.

---

# 3. Calibration Discipline

Calibration activities include:

- Slip identification
- Traction curve fitting
- Sinkage model estimation
- Estimator covariance tuning
- Control limit validation

Each calibration experiment must include:

- Formal specification
- Defined signals
- Explicit loss function
- Acceptance criteria
- Output parameter files
- Stored plots and summary report

No tuning based on visual inspection is permitted.

---

# 4. Data Integrity Requirements

Analysis consumes datasets from:

`/datasets/<run_id>/`

Each dataset must include:

- run_metadata.json
- run.mcap (or equivalent)
- metrics.json (if available)

All datasets are immutable.

Analysis scripts must never overwrite raw data.

---

# 5. Reproducibility Standard

Every analysis result must be reproducible with:

- Same dataset
- Same git commit
- Same parameter file
- Same random seed (if stochastic)

Reproducibility includes:

- Identical parameter outputs (within tolerance)
- Identical summary metrics
- Identical figures (numerically equivalent)

All analysis scripts must produce deterministic output.

---

# 6. Parameter Governance

Calibrated parameters must be exported to:

`analysis/calibration/configs/`

After validation, approved parameters are promoted to:

`configs/`

Promotion requires:

- Documented experiment reference
- Quantified improvement
- Regression confirmation
- Peer review (if multi-maintainer)

No parameter changes without documented evidence.

---

# 7. Statistical Evaluation

Performance evaluation must include:

- Mean error
- Standard deviation
- Worst-case deviation
- Confidence intervals (if applicable)

Single-run improvements are insufficient.

Improvements must be statistically supported.

---

# 8. Reporting Requirements

Each calibration experiment must produce:

- YAML parameter file
- Structured summary report (Markdown or PDF)
- Supporting figures
- Version and dataset reference

Reports must include:

- Objective
- Method
- Results
- Limitations
- Recommendation

---

# 9. Tooling Principles

All analysis code must:

- Use explicit units (SI only)
- Avoid hidden constants
- Version parameter files
- Log intermediate values when fitting
- Fail loudly when assumptions are violated

Notebooks are permitted for exploration,
but final calibration must be implemented in reproducible scripts.

---

# 10. Engineering Philosophy

Analysis is the bridge between:

Physics  
Control  
Autonomy  

It enforces reality against simulation optimism.

Confidence does not come from smooth plots.

Confidence comes from:

- Quantified error
- Controlled experiments
- Deterministic repetition
- Documented uncertainty

---

# 11. Maturity Objective

The long-term objective of the analysis framework is to enable:

- Continuous model refinement
- Automated parameter validation
- Dataset-driven regression comparison
- Scientific defensibility of mobility behavior
