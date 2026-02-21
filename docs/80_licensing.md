# Licensing

This project separates licensing by artifact type.

Each category is governed independently to ensure clarity
for contributors, users, and downstream adopters.

---

# 1. Software

Includes:

- ROS 2 packages
- Python scripts
- Control logic
- Estimation modules
- Planning and autonomy code
- Simulation integration code
- CI workflows

License:

-> Apache License 2.0

Rationale:

- Permissive, industry-friendly
- Allows commercial use
- Protects contributors through patent grant
- Widely adopted in robotics ecosystems

See:

/LICENSES/software/Apache-2.0.txt

---

# 2. Hardware

Includes:

- CAD models
- URDF geometry source files
- Mechanical drawings
- PCB designs
- Fabrication files
- Electrical schematics

License:

-> CERN Open Hardware License v2 – Weakly Reciprocal (CERN-OHL-W-2.0)

Rationale:

- Encourages modification and redistribution
- Requires documentation of changes
- Protects openness of physical designs
- Appropriate for research-grade hardware

See:

/LICENSES/hardware/CERN-OHL-W-2.0.txt

---

# 3. Datasets

Includes:

- MCAP logs
- metrics.json
- run_metadata.json
- Calibration datasets
- Regression datasets

License:

-> Creative Commons Attribution 4.0 International (CC-BY-4.0)

Rationale:

- Allows reuse and redistribution
- Requires attribution
- Enables academic citation
- Suitable for research dissemination

See:

/LICENSES/data/CC-BY-4.0.txt

---

# 4. Third-Party Dependencies

External libraries and frameworks
retain their original licenses.

This includes:

- ROS 2
- Gazebo
- Webots
- PyBullet
- Nav2
- robot_localization
- MCAP

Users are responsible for complying
with upstream license terms.

---

# 5. Contribution Policy

By submitting contributions, contributors agree that:

- Software contributions are licensed under Apache 2.0.
- Hardware contributions are licensed under CERN-OHL-W-2.0.
- Dataset contributions are licensed under CC-BY-4.0.

No contribution may introduce incompatible licensing.

---

# 6. Patent and Liability Notice

Software components under Apache 2.0 include
an explicit patent license grant.

All components are provided:

"AS IS", without warranty of any kind.

The project maintainers are not liable
for damages arising from use of:

- Software
- Hardware designs
- Datasets

---

# 7. Summary

Software  -> Apache License 2.0  
Hardware  -> CERN-OHL-W-2.0  
Datasets  -> CC-BY-4.0  

See `/LICENSES` for full license texts.
