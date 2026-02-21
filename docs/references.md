# References

This document lists the primary technical references
supporting the models, control architecture,
estimation framework, and terramechanics formulations
used in this project.

All models implemented in this repository trace back
to established literature.

---

# 1. Historical Context

PrOP-M Mars Rover

- Soviet Mars 2 and Mars 3 missions (1971)
- PrOP-M tethered micro-rover concept
- Early planetary mobility experiments

Primary reference:

Avduevsky, V. S., et al.  
"Scientific Equipment of the Mars-3 Automatic Station."  
Space Research, 1973.

---

# 2. Rover Mobility and Terramechanics

Bekker, M. G.  
Introduction to Terrain-Vehicle Systems.  
University of Michigan Press, 1969.

Wong, J. Y.  
Theory of Ground Vehicles. 4th Edition.  
John Wiley & Sons, 2008.

Wong, J. Y., and Reece, A. R.  
"Prediction of Rigid Wheel Performance Based on the Analysis of Soil–Wheel Stresses."  
Journal of Terramechanics, 1967.

Iagnemma, K., and Dubowsky, S.  
Mobile Robots in Rough Terrain.  
Springer Tracts in Advanced Robotics, 2004.

---

# 3. Planetary Rover Design

NASA Jet Propulsion Laboratory.

Maimone, M., Cheng, Y., and Matthies, L.  
"Two Years of Visual Odometry on the Mars Exploration Rovers."  
Journal of Field Robotics, 2007.

Lindemann, R. A., and Voorhees, C. J.  
"Mars Exploration Rover Mobility Assembly Design."  
IEEE Aerospace Conference, 2005.

---

# 4. Control Theory

Åström, K. J., and Murray, R. M.  
Feedback Systems: An Introduction for Scientists and Engineers.  
Princeton University Press, 2008.

Franklin, G. F., Powell, J. D., and Emami-Naeini, A.  
Feedback Control of Dynamic Systems.  
Pearson.

---

# 5. State Estimation

Thrun, S., Burgard, W., and Fox, D.  
Probabilistic Robotics.  
MIT Press, 2005.

Maybeck, P. S.  
Stochastic Models, Estimation, and Control.  
Academic Press, 1979.

Bar-Shalom, Y., Li, X. R., and Kirubarajan, T.  
Estimation with Applications to Tracking and Navigation.  
Wiley, 2001.

---

# 6. Navigation and Planning

LaValle, S. M.  
Planning Algorithms.  
Cambridge University Press, 2006.

Macenski, S., et al.  
"The Nav2 Behavior Tree Navigator."  
ROS 2 Navigation Stack Documentation.

---

# 7. Simulation and Robotics Frameworks

ROS 2 Documentation  
https://docs.ros.org

Gazebo Documentation  
https://gazebosim.org

Webots Documentation  
https://cyberbotics.com

PyBullet Documentation  
https://pybullet.org

MCAP Format Specification  
https://mcap.dev

---

# 8. Engineering and Systems Discipline

NASA Systems Engineering Handbook  
NASA/SP-2007-6105 Rev2

NASA Technical Standard  
"Software Assurance and Software Safety"

“Test what you fly, fly what you test.”  
NASA Engineering Principle

---

# 9. Notes

All implemented models in this repository:

- Follow established literature
- Clearly document deviations
- State assumptions explicitly
- Provide parameter traceability

No proprietary or undocumented models are used.

Future extensions must cite relevant literature
before integration.
