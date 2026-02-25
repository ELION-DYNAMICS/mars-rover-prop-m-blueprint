# SoilProbe
# Soil probe measurements for terramechanics calibration and science.
# SI units only.

builtin_interfaces/Time stamp
string frame_id

# Probe state
bool engaged               # probe currently inserted / operating
float32 depth_m            # penetration depth (m), 0 if not inserted
float32 insertion_rate_mps # penetration speed (m/s)

# Forces
float32 axial_force_n      # force along probe axis (N)
float32 lateral_force_n    # net lateral force magnitude (N)

# Optional environment readings
float32 temperature_c      # degC (NaN if unavailable)
float32 moisture_ratio     # 0..1 (NaN if unavailable)

# Quality
float32 confidence         # 0..1
string notes
