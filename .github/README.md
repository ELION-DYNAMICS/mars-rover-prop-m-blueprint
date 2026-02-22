# Repository Governance and Automation

This document describes how this repository is managed.

It defines:

- Continuous Integration policy
- Pull Request requirements
- Issue handling standards
- Regression enforcement
- Contribution expectations

This project follows structured engineering discipline.
Automation enforces quality.

---

# 1. Continuous Integration (CI)

All pull requests to `main` must pass:

- `ci_colcon.yml` -> Build + test
- `docs_build.yml` -> Documentation validation
- `sim_regression.yml` -> Simulation regression (if applicable)

A PR cannot be merged if any workflow fails.

CI is authoritative.
Local success does not override CI failure.

---

# 2. Simulation Regression

Simulation regression validates:

- Deterministic behavior (fixed seed)
- Mission completion
- Slip thresholds
- Tether boundary compliance
- Recovery behavior limits

Regression thresholds are defined in:

`scenarios/<scenario>/scenario.yaml`

If metrics degrade, the PR must justify and document the change.

No silent performance regression allowed.

---

# 3. Pull Request Policy

Every PR must include:

- Clear summary
- Linked issue or requirement
- Verification steps
- Evidence (logs, run_id, metrics)
- ICD impact declaration (if applicable)

If interfaces change, the following must be updated:

- `docs/interface_control_document.md`
- Related message definitions
- Regression scenarios (if affected)

PRs without evidence will not be merged.

---

# 4. Issue Policy

Issue types:

- Bug
- Feature
- Engineering Task
- Question

Bug reports must include:

- Reproduction steps
- Version/commit
- Environment
- Logs or run_id

If it cannot be reproduced, it cannot be fixed.

---

# 5. Interface Stability

Topics, frames, units, and message types are contracts.

Any modification requires:

- ICD update
- Documentation update
- Regression validation

No implicit changes permitted.

---

# 6. Determinism Requirement

Simulation runs used for regression must:

- Use fixed random seed
- Use fixed scenario parameters
- Use deterministic physics configuration

If results change under identical inputs,
investigation is required.

---

# 7. Dataset Integrity

All regression runs must produce:

- MCAP log
- run_metadata.json
- metrics.json

Datasets are immutable.

If parameters change,
a new run_id must be generated.

---

# 8. Coding Standards

- SI units only
- No hidden constants
- Parameters in YAML, not hard-coded
- No autonomy → actuator shortcuts
- Safety overrides always enforced

---

# 9. Documentation Standard

New subsystems require:

- Documentation in `docs/`
- Reference citations (if model-based)
- V&V acceptance criteria

Code without documentation is incomplete.

---

# 10. Engineering Principle

“Test what you fly, fly what you test.”

All simulation logic must mirror hardware interfaces.
No simulation-only shortcuts in autonomy or control layers.

---

# 11. Maintainer Authority

Maintainers may:

- Request additional evidence
- Require regression expansion
- Reject undocumented behavior changes
- Enforce architectural consistency

The goal is reliability, not speed of merge.
