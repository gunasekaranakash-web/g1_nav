#!/usr/bin/env python3
"""G1 Robot Connector - bridges ROS2 to G1 via Unitree SDK."""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient


class G1RobotConnector(Node):
    def __init__(self):
        super().__init__("g1_robot_connector")

        self.declare_parameter("interface", "enp5s0")
        interface = self.get_parameter("interface").value

        self.get_logger().info(f"Initializing Unitree SDK on: {interface}")
        ChannelFactoryInitialize(0, interface)

        self.loco_client = LocoClient()
        self.loco_client.SetTimeout(10.0)
        self.loco_client.Init()
        self.get_logger().info("Connected to G1 loco client!")

        self.cmd_vel_sub = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_vel_callback, 10
        )
        self.status_pub = self.create_publisher(String, "/g1/status", 10)
        self.create_timer(1.0, self.publish_status)
        self.get_logger().info("G1 Robot Connector ready!")

    def cmd_vel_callback(self, msg):
        vx = msg.linear.x
        vy = msg.linear.y
        vyaw = msg.angular.z
        self.loco_client.Move(vx, vy, vyaw)
        self.get_logger().info(f"Move: vx={vx:.2f} vy={vy:.2f} vyaw={vyaw:.2f}")

    def publish_status(self):
        msg = String()
        msg.data = "Connected"
        self.status_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = G1RobotConnector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
