cmake_minimum_required(VERSION 3.8)
project(rover_sim_gazebo)

find_package(ament_cmake REQUIRED)
find_package(gazebo REQUIRED)

add_subdirectory(plugins)

install(DIRECTORY
  launch
  worlds
  models
  config
  DESTINATION share/${PROJECT_NAME}
)

install(FILES README.md
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
