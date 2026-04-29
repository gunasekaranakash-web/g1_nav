# g1_nav (Wired)

ROS2 Humble autonomous navigation stack for the **Unitree G1 humanoid robot** — wired Ethernet edition.

## Features
- 🤖 `cmd_vel` control of G1 via Unitree SDK
- 🦿 23-DOF joint state publishing
- 🧭 Real-time odometry (500Hz)
- 🗺️ SLAM mapping with slam_toolbox + Mid360 LiDAR
- 📍 AMCL localization
- 🎯 Nav2 autonomous goals

## Requirements
- Ubuntu 22.04 + ROS2 Humble
- Unitree G1 (motion service running)
- Livox Mid360 LiDAR
- Ethernet to G1 (192.168.123.x)

## Custom Nodes
| Node | Purpose |
|------|---------|
| `robot_connector.py` | ROS2 `cmd_vel` → G1 SDK |
| `joint_publisher.py` | G1 joint states → `/joint_states` |
| `odom_publisher.py` | G1 `rt/odommodestate` → `/odom` + TF |

## Build
```bash
git clone https://github.com/gunasekaranakash-web/g1_nav.git
cd g1_nav
colcon build --symlink-install
source install/setup.bash
```

## Usage (3 terminals)

**Prereq:** `~/.bashrc` sets `ROS_DOMAIN_ID=0` and `ROS_LOCALHOST_ONLY=1`.

```bash
# Terminal 1
ros2 launch livox_ros_driver2 msg_MID360_launch.py

# Terminal 2
ros2 launch g1_nav bringup.launch.py

# Terminal 3
ros2 launch g1_nav nav2.launch.py
```

In RViz: **2D Pose Estimate** → **Nav2 Goal** → robot walks!

## Engineering Notes
- LiDAR mounted upside-down → 180° roll TF
- Use `rt/odommodestate` (not `rt/sportmodestate`)
- TF: `map → odom → pelvis → sensors` (REP-105)
- ROS_LOCALHOST_ONLY isolates ROS2 traffic; SDK handles G1 comms

## Wireless Version
See companion repo: [g1_nav_wireless](https://github.com/gunasekaranakash-web/g1_nav_wireless) (WIP)

## Author
Akash Gunasekaran

## License
MIT
