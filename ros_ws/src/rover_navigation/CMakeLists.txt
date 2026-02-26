cmake_minimum_required(VERSION 3.8)
project(rover_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  params
  DESTINATION share/${PROJECT_NAME}
)

install(FILES README.md
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
