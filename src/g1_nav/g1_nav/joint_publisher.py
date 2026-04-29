#!/usr/bin/env python3
"""Subscribe to G1 lowstate via Unitree SDK and publish /joint_states."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

# 23DOF joint mapping: ROS joint name -> motor index in G1's 29DOF lowstate
# Based on g1pilot's G1JointIndex but skipping the 6 joints not in 23DOF URDF
G1_JOINT_MAP = [
    ("left_hip_pitch_joint", 0),
    ("left_hip_roll_joint", 1),
    ("left_hip_yaw_joint", 2),
    ("left_knee_joint", 3),
    ("left_ankle_pitch_joint", 4),
    ("left_ankle_roll_joint", 5),
    ("right_hip_pitch_joint", 6),
    ("right_hip_roll_joint", 7),
    ("right_hip_yaw_joint", 8),
    ("right_knee_joint", 9),
    ("right_ankle_pitch_joint", 10),
    ("right_ankle_roll_joint", 11),
    ("waist_yaw_joint", 12),
    # Skip 13 (waist_roll), 14 (waist_pitch) - not in 23DOF URDF
    ("left_shoulder_pitch_joint", 15),
    ("left_shoulder_roll_joint", 16),
    ("left_shoulder_yaw_joint", 17),
    ("left_elbow_joint", 18),
    ("left_wrist_roll_joint", 19),
    # Skip 20 (left_wrist_pitch), 21 (left_wrist_yaw) - not in 23DOF URDF
    ("right_shoulder_pitch_joint", 22),
    ("right_shoulder_roll_joint", 23),
    ("right_shoulder_yaw_joint", 24),
    ("right_elbow_joint", 25),
    ("right_wrist_roll_joint", 26),
    # Skip 27, 28
]

JOINT_NAMES = [name for name, _ in G1_JOINT_MAP]
MOTOR_INDICES = [idx for _, idx in G1_JOINT_MAP]


class JointPublisher(Node):
    def __init__(self):
        super().__init__("joint_publisher")

        self.declare_parameter("interface", "enp5s0")
        interface = self.get_parameter("interface").value

        self.get_logger().info(f"Initializing Unitree SDK on: {interface}")
        try:
            ChannelFactoryInitialize(0, interface)
        except Exception:
            pass

        self.pub = self.create_publisher(JointState, "/joint_states", 10)

        self.sub = ChannelSubscriber("rt/lowstate", LowState_)
        self.sub.Init(self.lowstate_callback, 10)
        self.get_logger().info("Subscribed to rt/lowstate")

    def lowstate_callback(self, msg: LowState_):
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = JOINT_NAMES
        js.position = [float(msg.motor_state[i].q) for i in MOTOR_INDICES]
        js.velocity = [float(msg.motor_state[i].dq) for i in MOTOR_INDICES]
        self.pub.publish(js)


def main(args=None):
    rclpy.init(args=args)
    node = JointPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
