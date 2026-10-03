# BluePilot custom1 installer bridge

Enter https://installer.comma.ai/MostlyClueless94/custom1 in Custom Software.

The standard comma installer clones this bootstrap branch. On first launch it downloads MostlyClueless94/bluepilot custom1, verifies commit 8e9d9c0f4711dace8aba613875f7110b6ae80497, replaces the bootstrap checkout, initializes submodules and launches BluePilot.

Both prototype settings are OFF by default, at Settings → BluePilot → Longitudinal Tuning:
- Concurrent Acceleration Prototype: bounded gas/cruise overlap in Experimental Mode.
- Follow Vehicle Speed Limits: camera-sign-based saved speed, including while cruise is paused. Set cruise to the recognized limit to arm. Manual +/- pauses following. Uses vehicle data without maps; Ford's dashboard can differ.

Enable sunnypilot Longitudinal Control (Alpha). For speed-limit following, use Cruise → Speed Limit → Info and Customize Source → Car Only. Restart after enabling a prototype setting. Longitudinal/Lateral Maneuver Mode and Joystick Debug Mode must be OFF.

Software/firmware focused checks pass; on-device and vehicle validation of the speed-limit feature remains outstanding. Source details: docs/BP_VEHICLE_SPEED_LIMIT_CRUISE.md in the BluePilot branch.
