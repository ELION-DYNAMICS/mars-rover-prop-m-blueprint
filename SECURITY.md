# Security Policy

## Scope

This repository contains robotics software, simulation environments, control logic, and dataset tooling related to a Mars rover architecture.

Security applies to:

- ROS 2 nodes and communication interfaces
- Simulation environments
- Docker containers
- CI/CD pipelines
- Dataset integrity
- Dependency management
- Hardware interface layers (if deployed on physical systems)

---

## Supported Versions

Only the latest tagged release and the `main` branch are supported with security updates.

Older versions may contain unpatched vulnerabilities.

---

## Reporting a Vulnerability

If you discover a security vulnerability:

1. Do NOT open a public issue.
2. Email the maintainers directly.
3. Provide:
   - Clear description of the issue
   - Reproduction steps
   - Impact assessment
   - Suggested mitigation (if available)

You will receive acknowledgment within 72 hours.

Responsible disclosure is expected.

---

## Threat Model

This project assumes the following threat surfaces:

### 1. ROS 2 Network Layer
- Unauthorized node injection
- Topic spoofing
- Parameter tampering

Mitigation:
- DDS security (SROS2) recommended for production
- Network isolation required for hardware deployment

### 2. Command Interfaces
- Malicious `/cmd_vel` injection
- Parameter override attacks

Mitigation:
- Validation layers in control nodes
- Rate limiting
- Watchdog enforcement

### 3. Supply Chain Risk
- Compromised dependencies
- Malicious container base images

Mitigation:
- Pinned dependency versions
- Verified Docker base images
- CI dependency scanning

### 4. Dataset Integrity
- Tampered MCAP logs
- Altered metrics files

Mitigation:
- Metadata schema validation
- Optional hash-based verification
- CI regression checks

---

## Secure Deployment Guidelines

If deploying beyond simulation:

- Isolate rover network
- Disable unused ROS interfaces
- Use SROS2
- Enforce read-only parameters where possible
- Implement hardware-level emergency stop
- Never expose raw ROS 2 ports to the public internet

---

## Safety Disclaimer

This repository is primarily simulation-oriented.

If adapted for physical robotic hardware:
- The maintainers assume no liability.
- Proper risk assessment must be performed.
- Independent safety review is mandatory.

Autonomous systems without fail-safes are engineering negligence.

---

## Cryptography

If cryptographic features are added:
- Use established libraries only
- No custom crypto
- No hardcoded secrets
- Use environment-based secret injection

---

## Security Philosophy

No autonomy system is complete without:
- Deterministic fallback
- Logging
- Isolation
- Failsafe shutdown
