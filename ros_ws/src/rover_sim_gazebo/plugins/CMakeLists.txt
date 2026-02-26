cmake_minimum_required(VERSION 3.8)
project(rover_sim_gazebo_plugins)

find_package(ament_cmake REQUIRED)

# Gazebo classic headers/libs
find_package(gazebo REQUIRED)

include_directories(
  include
  ${GAZEBO_INCLUDE_DIRS}
)

link_directories(${GAZEBO_LIBRARY_DIRS})

add_library(terrain_preset_plugin SHARED
  src/terrain_preset_plugin.cpp
)

target_link_libraries(terrain_preset_plugin
  ${GAZEBO_LIBRARIES}
)

install(TARGETS terrain_preset_plugin
  LIBRARY DESTINATION lib
)

ament_package()
