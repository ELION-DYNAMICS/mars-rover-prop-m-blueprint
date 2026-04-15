add_library(terrain_preset_plugin SHARED
  src/terrain_preset_plugin.cpp
)

target_include_directories(terrain_preset_plugin PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${GAZEBO_INCLUDE_DIRS}
)

link_directories(${GAZEBO_LIBRARY_DIRS})

target_link_libraries(terrain_preset_plugin
  ${GAZEBO_LIBRARIES}
)

install(TARGETS terrain_preset_plugin
  LIBRARY DESTINATION lib
)
