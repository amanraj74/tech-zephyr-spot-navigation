# Tech Zephyr 3.0 - Autonomous Spot Navigation
**Team DeepLearners | Aman Jaiswal**

## Overview
Autonomous Spot robot navigation with sequential waypoints (A→B→C→D), obstacle avoidance, and zero collision guarantee.

## Features
- Sequential waypoint navigation
- Real-time LiDAR obstacle detection
- Adaptive speed control
- Autonomous recovery system

## Quick Start
colcon build --symlink-install
source install/setup.bash
ign gazebo -r src/spot_navigation/worlds/empty_room-2.sdf
ros2 run spot_navigation spot_navigator

text

## Author
Aman Jaiswal | aerraj50@gmail.com | Team DeepLearners
