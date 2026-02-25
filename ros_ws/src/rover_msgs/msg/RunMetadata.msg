# RunMetadata
# Minimal on-wire run metadata for traceability.
# Full run metadata still lives in run_metadata.json in datasets/.
# SI units only.

builtin_interfaces/Time stamp

# Run identity
string run_id              # recommended: YYYYMMDD_HHMMSS_<scenario>_<git_short_hash>
string mode                # "simulation" | "hardware"
string backend             # "gazebo" | "webots" | "pybullet" | "hardware"
string scenario

uint32 seed                # 0 for hardware unless intentionally used

# Git identity
string git_commit          # full or short hash
bool git_dirty
string git_branch

# Timing/physics
bool use_sim_time
float32 time_step_s
float32 real_time_factor

# Config references (paths or identifiers)
string control_config
string estimator_config
string terramechanics_config
string nav2_profile

# Notes
string operator
string notes
