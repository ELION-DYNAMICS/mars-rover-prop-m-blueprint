# infrastructure/docker

Docker images for the rover program.

Images:
- Dockerfile.dev: interactive developer image (build tools + ROS + Gazebo)
- Dockerfile.ci: CI image for deterministic build/test in GitHub Actions
- Dockerfile.runtime: minimal runtime image (no compilers) for running nodes

Principles:
- Pin the OS and ROS distribution.
- Separate build-time and run-time concerns.
- CI must run headless and produce the same artifacts every time.

Usage:
- docker compose build
- docker compose run dev
- docker compose run ci
