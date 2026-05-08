# 🤖 g1_nav (Wired)

> ROS2 Humble autonomous navigation stack for the **Unitree G1 humanoid robot** — wired Ethernet edition.

Built from scratch by bridging G1's proprietary Unitree SDK to the standard ROS2 / Nav2 ecosystem. Click any point on a map → G1 plans a path and walks there autonomously. 🚶

---

## ✨ Features

- 🤖 **cmd_vel control** of G1 via Unitree SDK
- 🦿 **23-DOF joint state publishing** to `/joint_states`
- 🧭 **Real-time odometry** at 500Hz from G1's `rt/odommodestate`
- 🗺️ **SLAM mapping** with slam_toolbox + Mid360 LiDAR
- 📍 **AMCL localization** on saved maps
- 🎯 **Nav2 autonomous navigation** (click-to-go in RViz)
- 📺 **Real-time RViz visualization** (robot model, LiDAR, odometry)

---

## 📋 Requirements

- 🐧 Ubuntu 22.04 + ROS2 Humble
- 🤖 Unitree G1 EDU (motion service running on PC1)
- 📡 Livox Mid360 LiDAR (mounted on G1's head, inverted)
- 🔌 Ethernet connection to G1

---

## 🛠️ Setup (First Time)

### 1️⃣ Install ROS2 Humble

Follow the official guide: [ROS2 Humble Installation](https://docs.ros.org/en/humble/Installation.html)

### 2️⃣ Install required ROS2 packages

```bash
sudo apt install -y \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-pointcloud-to-laserscan
```

### 3️⃣ Install Unitree SDK (Python)

```bash
cd ~
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip install -e .
```

> 💡 If you get a `Could not locate cyclonedds` error, run:
> ```bash
> pip install cyclonedds==0.10.2
> ```

### 4️⃣ Install Livox ROS Driver 2

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/Livox-SDK/livox_ros_driver2.git
cd livox_ros_driver2
./build.sh humble
```

### 5️⃣ Configure your laptop's static Ethernet IP 🔌

Connect Ethernet cable from your laptop to G1's RJ45 port. Set a static IP on the same subnet as G1 (refer to Unitree's official documentation for the correct subnet).

**🖥️ Option A — GUI (recommended)**

1. Open **Settings → Network**
2. Click the ⚙️ gear icon next to your wired connection
3. Go to the **IPv4** tab
4. Change method from `Automatic (DHCP)` → **`Manual`**
5. Add an Address:
   - 📍 **Address:** a free IP on G1's subnet
   - 🎭 **Netmask:** `255.255.255.0`
   - 🚪 **Gateway:** *(leave empty)*
6. Click **Apply**, then toggle the connection off and on

**⌨️ Option B — Command line**

```bash
# Find your interface name first
ip addr | grep -E "enp|eth"

# Set static IP (replace placeholders)
sudo ip addr add YOUR_STATIC_IP/24 dev YOUR_INTERFACE
sudo ip link set YOUR_INTERFACE up
```

> ⚠️ Command-line method doesn't persist after reboot. Use GUI for permanent setup.

✅ **Verify connection** by pinging G1's onboard computer.

### 6️⃣ Find your Ethernet interface name

```bash
ip addr | grep -E "enp|eth"
```

Note the name (e.g., `enp5s0`, `eth0`, `enp3s0`).

> 💡 The default in this repo is **`enp5s0`** — if yours differs, you'll pass it at launch (no code edits needed).

### 7️⃣ Add to `~/.bashrc`

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=0
export ROS_LOCALHOST_ONLY=1
```

Then reload:
```bash
source ~/.bashrc
```

### 8️⃣ Clone and build this package

```bash
cd ~
git clone https://github.com/gunasekaranakash-web/g1_nav.git
cd g1_nav
colcon build --symlink-install
source install/setup.bash
```

🎉 **Setup complete!**

---

## 🧩 Custom Nodes

| Node | Purpose |
|------|---------|
| 🚗 `robot_connector.py` | ROS2 `cmd_vel` → G1 SDK `LocoClient.Move()` |
| 🦿 `joint_publisher.py` | Reads G1's `rt/lowstate`, publishes 23-DOF `/joint_states` |
| 🧭 `odom_publisher.py` | Reads G1's `rt/odommodestate` (500Hz), publishes `/odom` + TF |

> 💡 All three nodes accept the network interface as a parameter (default: `enp5s0`).

---

## 🚀 Usage

### 📺 A. Real-time RViz Visualization Only

Just shows the robot model, LiDAR pointcloud, and live odometry — no mapping or navigation.

```bash
# Terminal 1 — LiDAR
ros2 launch livox_ros_driver2 msg_MID360_launch.py

# Terminal 2 — Bringup (opens RViz)
ros2 launch g1_nav bringup.launch.py
```

🔧 If your interface isn't `enp5s0`:
```bash
ros2 launch g1_nav bringup.launch.py interface:=YOUR_INTERFACE
```

🎬 **In RViz you'll see:**
- 🤖 G1 robot model
- 🟢 360° LiDAR pointcloud
- 🦿 Real-time joint motion
- 📍 Odometry updating as G1 walks

---

### 🗺️ B. Build a Map (SLAM)

```bash
# Terminal 1 — LiDAR
ros2 launch livox_ros_driver2 msg_MID360_launch.py

# Terminal 2 — Bringup
ros2 launch g1_nav bringup.launch.py

# Terminal 3 — SLAM
ros2 launch g1_nav slam.launch.py
```

🎮 Drive G1 manually around the room using the Unitree remote controller. Watch the map build in RViz in real-time.

💾 **Save the map** when you're happy with it:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/g1_nav/src/g1_nav/maps/my_room
```

🔨 **Rebuild** so the map is installed:
```bash
cd ~/g1_nav
colcon build --symlink-install
source install/setup.bash
```

---

### 🎯 C. Autonomous Navigation

> ⚠️ Requires a saved map (see section B).

```bash
# Terminal 1 — LiDAR
ros2 launch livox_ros_driver2 msg_MID360_launch.py

# Terminal 2 — Bringup
ros2 launch g1_nav bringup.launch.py

# Terminal 3 — Nav2
ros2 launch g1_nav nav2.launch.py
```

⏱️ Wait until Terminal 3 shows **`Managed nodes are active`**.

🖱️ **In RViz:**
1. Set **Fixed Frame** = `map` (top-left, under Global Options)
2. Click **2D Pose Estimate** → click G1's actual location → drag to set facing direction
3. Wait until Navigation panel shows ✅ **Localization: active**
4. Click **Nav2 Goal** → click free space → drag direction → release
5. 🤖 **G1 plans a path and walks there autonomously!**

> 🛑 **Safety:** Keep the Unitree remote controller ready (`L2+B` = emergency stop). Make sure G1 has clear floor space.

---

## ⚙️ Configuration

### 🌐 Network interface
Default is `enp5s0`. Override at launch:
```bash
ros2 launch g1_nav bringup.launch.py interface:=YOUR_INTERFACE
```

### 🎚️ Nav2 parameters
Tuned for G1 humanoid in `src/g1_nav/config/nav2_params.yaml`:
- 📏 `robot_radius: 0.3`
- 🚶 `max_vel_x: 0.3` (G1's walking speed)
- 🔄 `max_vel_theta: 0.5`
- 🛡️ `inflation_radius: 0.25`
- 🤸 AMCL `OmniMotionModel` (G1 can strafe sideways)
- 🦴 Base frame: `pelvis`

### 📡 LiDAR processing (pointcloud → laserscan)
Configured in `bringup.launch.py`:
- 📐 `min_height: -0.3`, `max_height: 1.5`
- 📏 `range_min: 0.3`, `range_max: 30.0`
- 🎯 Target frame: `pelvis`

---

## 🌳 TF Tree (REP-105)

```
map
└── odom                          (AMCL during nav, slam_toolbox during mapping)
    └── pelvis                   (odom_publisher, 500Hz)
        ├── 23 G1 joint links   (robot_state_publisher from URDF)
        ├── mid360_link
        │    └── livox_frame    (180° roll — LiDAR mounted upside-down)
        └── ...
```

---

## 🔧 Engineering Notes

- 🙃 **LiDAR is mounted upside-down** on G1's head — a static TF applies 180° roll to correct it
- ⚠️ **Use `rt/odommodestate`** (NOT `rt/sportmodestate`, despite some Unitree docs)
- 🎚️ **23-DOF mapping:** G1's `rt/lowstate` has 29 motor slots, but only 23 correspond to URDF joints
- 🔒 **`ROS_LOCALHOST_ONLY=1`** keeps your laptop's ROS2 traffic on localhost; the Unitree SDK handles G1 communication separately on Ethernet via DDS Domain 0
- ⚡ **No cmd_vel translation needed** — `robot_connector.py` directly calls `LocoClient.Move(vx, vy, vyaw)`

---

## 🚨 Troubleshooting

| 😵 Symptom | 🔧 Fix |
|------------|--------|
| Nodes start but G1 unresponsive | Verify motion_service running on G1's PC1; check Ethernet ping |
| `unitree_sdk2_python` import error | `pip install cyclonedds==0.10.2`, then re-install SDK |
| `ChannelFactoryInitialize` hangs | Wrong network interface — pass `interface:=YOUR_INTERFACE` |
| LiDAR not in RViz | Check `/livox/lidar` is publishing: `ros2 topic hz /livox/lidar` |
| AMCL "extrapolation" errors | Wait 10+ seconds between Terminal 2 and Terminal 3 launches |
| Path planning fails | Reduce `inflation_radius`, click goals in clearly free (white) areas |

---

## 👤 Author

**Akash Gunasekaran**

🐙 GitHub: [@gunasekaranakash-web](https://github.com/gunasekaranakash-web)

---

## 📜 License

MIT

---

> ⭐ If you found this useful, leave a star on the repo!
