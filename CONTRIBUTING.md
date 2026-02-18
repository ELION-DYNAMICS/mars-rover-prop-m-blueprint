# Contributing Guidelines

Thank you for contributing to the Mars Rover PROP-M Blueprint.

This repository follows strict engineering discipline. Contributions are welcome - but must meet reproducibility, documentation, and validation standards.

---

## Core Principles

1. Simulation-first development  
2. No feature without measurable output  
3. No autonomy without logging  
4. No undocumented parameters  
5. No merge without CI passing  

If a change cannot be tested, logged, or explained - it will not be merged.

---

## Contribution Types

We accept:

- Bug fixes
- Performance improvements
- Control algorithm enhancements
- Navigation improvements
- Simulation realism upgrades
- Documentation improvements
- Scenario expansions
- Dataset validation tools

We do not accept:

- Unverified “cool demos”
- Breaking architectural changes without justification
- Unlicensed external assets
- Untested control logic

---

## Workflow

### 1. Fork and Branch

Create a feature branch:

feature/<short-description>


Examples:

feature/slip-estimator
feature/tether-constraint-fix
feature/nav2-parameter-tuning


Bug fixes:

fix/<short-description>


---

### 2. Coding Standards

- Follow ROS 2 conventions
- Use meaningful parameter names
- Document all tunable parameters
- Add inline comments for non-trivial logic
- Keep launch files readable

C++:
- Follow ament lint rules
- No unused variables
- No silent failure handling

Python:
- PEP8 compliant
- Type hints where reasonable
- Explicit exception handling

---

### 3. Testing Requirements

All contributions must include:

- Unit tests (if algorithmic)
- Updated launch tests (if system-level)
- Scenario validation (if behavior changes)

If your change affects motion, navigation, or estimation:
- Provide before/after metrics.

Regression scenarios must still pass.

---

### 4. Logging & Reproducibility

If your feature affects runtime behavior:

- Ensure rosbag2 (MCAP) compatibility
- Update dataset schema if necessary
- Document new metrics in `/docs/70_datasets.md`

No undocumented runtime changes.

---

### 5. Documentation

Update:

- Relevant files in `/docs`
- Parameter explanations
- Architecture diagrams (if impacted)

Engineering clarity > cleverness.

---

### 6. Pull Request Checklist

Before submitting a PR, confirm:

- [ ] Code builds locally
- [ ] Tests pass
- [ ] CI passes
- [ ] Documentation updated
- [ ] No unused parameters
- [ ] No debug prints left behind
- [ ] Licensing headers present (if new files)

Incomplete PRs will not be reviewed.

---

## Issue Reporting

When filing issues, include:

- Scenario used
- ROS 2 distribution
- Commit hash
- Log excerpts
- Expected behavior
- Observed behavior

“Doesn’t work” is not actionable.

---

## Architecture Changes

Major architectural proposals require:

- A design document in `/docs/proposals`
- Problem statement
- Alternatives considered
- Impact analysis
- Migration plan

Stability is prioritized over novelty.

---

## Conduct

Professional and technical discussions only.

Disagreements are resolved through:
- Data
- Metrics
- Reproducible tests

Not opinions.

---

## Final Note

_This project aims to model space-grade engineering discipline. Every merged line should improve robustness, clarity, or reproducibility._

_If in doubt:
Measure first. Merge later._
