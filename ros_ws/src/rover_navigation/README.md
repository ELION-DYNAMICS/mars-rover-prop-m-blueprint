# rover_navigation

Navigation2 configuration package.

Contains:
- Modern mode Nav2 profile
- PROP-M conservative Nav2 profile
- Shared costmap parameter fragments
- Planner/controller plugin wiring

Policy:
- Nav2 must publish /cmd_vel (or equivalent)
- rover_control is responsible for shaping into /cmd_vel_safe
- rover_navigation must not enforce physics limits (that belongs to control)

Frames:
- map
- odom
- base_link

Inputs expected:
- /tf
- /tf_static
- /odometry/filtered
- a costmap sensor source (added later: lidar, depth, stereo, or simulated obstacles)
