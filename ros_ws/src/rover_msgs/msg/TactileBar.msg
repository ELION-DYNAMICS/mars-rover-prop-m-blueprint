# TactileBar
# One tactile bar/whisker element contact estimate.
# SI units only.

builtin_interfaces/Time stamp
string frame_id

# Identifier within an array (e.g., "front_left", "rear_right")
string id

# Contact state
bool contact

# Estimated contact normal force (N), if available (0 if unknown)
float32 normal_force_n

# Estimated contact point in bar frame (m), if available
geometry_msgs/Point contact_point_m

# Confidence in [0..1] (1 = high confidence)
float32 confidence
