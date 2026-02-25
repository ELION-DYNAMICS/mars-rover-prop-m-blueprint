# rover_estimation

This package provides the state estimation layer using `robot_localization` EKF.

Outputs:
- `/odometry/filtered` (nav_msgs/Odometry)
- TF: `odom -> base_link`

Inputs (baseline):
- `/wheel/odometry_raw` (wheel-derived odometry / twist)
- `/imu/data` (yaw rate z)

## Frame Tree Contract

This project enforces a strict minimal tree:

map (optional, Nav2/SLAM)
 -> odom (continuous, locally smooth)
    -> base_link (robot body)

Rules:
- Estimator owns `odom -> base_link`
- Mapping/SLAM (if enabled) owns `map -> odom`
- Drivers / simulation may publish sensor frames (imu_link, wheel frames) under base_link

No other node may publish `odom -> base_link`.
