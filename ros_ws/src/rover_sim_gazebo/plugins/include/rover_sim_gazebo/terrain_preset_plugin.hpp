#pragma once

#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>

namespace rover_sim_gazebo
{
class TerrainPresetPlugin : public gazebo::WorldPlugin
{
public:
  void Load(gazebo::physics::WorldPtr world, sdf::ElementPtr sdf) override;

private:
  void ApplyFriction(gazebo::physics::ModelPtr model,
                     const std::string &link_name,
                     double mu,
                     double mu2,
                     double restitution);

  gazebo::physics::WorldPtr world_;
};
}  // namespace rover_sim_gazebo
