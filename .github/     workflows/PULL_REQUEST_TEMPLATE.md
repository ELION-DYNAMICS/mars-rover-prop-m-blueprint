# Pull Request

## Summary
Describe what this PR changes and why.

- What problem does this solve?
- What subsystem(s) are affected?

---

## Type of Change
Check all that apply:

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor / cleanup (no functional change)
- [ ] Documentation
- [ ] Simulation / scenario update
- [ ] Model update (kinematics / dynamics / terramechanics)
- [ ] Control / estimation update
- [ ] CI / tooling

---

## Requirements & Traceability
Link the requirement, spec, or issue driving this change.

- Issue: #
- Spec / Doc (path): `docs/...`
- Requirement ID (if applicable):

---

## Interface Impact (ICD)
If anything below changes, update `docs/interface_control_document.md`.

- [ ] Topics added/changed
- [ ] Message definitions added/changed (`rover_msgs`)
- [ ] QoS changed
- [ ] Frame tree changed (`tf`)
- [ ] Units or timestamp behavior changed

Details:

---

## Verification (V&V Evidence)
Provide commands and evidence. “It works on my machine” is not evidence.

### Local Commands Run
- [ ] `colcon build`
- [ ] `colcon test`
- [ ] Lint (if applicable)

Commands executed (paste exact):

```bash
# example:
# colcon build --symlink-install
# colcon test
# colcon test-result --verbose
