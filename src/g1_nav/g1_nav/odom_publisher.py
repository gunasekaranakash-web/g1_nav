#!/usr/bin/env python3
"""
G1 Odometry Publisher
Subscribes to G1's rt/odommodestate via Unitree SDK DDS (high-freq, 500Hz)
Falls back to rt/lf/odommodestate (low-freq, 20Hz) if needed.

Publishes:
  - /odom topic (nav_msgs/Odometry)
  - TF: odom -> pelvis (dynamic, updates as robot walks)
"""

import math
import sys
import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_


class G1OdomPublisher(Node):
    def __init__(self):
        super().__init__('g1_odom_publisher')

        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'pelvis')
        self.declare_parameter('publish_rate', 50.0)

        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value

        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.latest_state = None
        self.msg_count = 0

        # Subscribe to G1's odometry topic (rt/odommodestate, NOT rt/sportmodestate)
        self.odom_state_sub = ChannelSubscriber(
            "rt/odommodestate", SportModeState_
        )
        self.odom_state_sub.Init(self.odom_state_handler, 10)

        self.timer = self.create_timer(
            1.0 / self.get_parameter('publish_rate').value,
            self.publish_odom
        )

        # Status timer to log if data is being received
        self.status_timer = self.create_timer(2.0, self.status_check)

        self.get_logger().info('G1 Odom Publisher started')
        self.get_logger().info('  Subscribing to: rt/odommodestate')
        self.get_logger().info('  odom_frame: ' + self.odom_frame)
        self.get_logger().info('  base_frame: ' + self.base_frame)

    def odom_state_handler(self, msg):
        self.latest_state = msg
        self.msg_count += 1

    def status_check(self):
        if self.latest_state is None:
            self.get_logger().warn('No data from rt/odommodestate yet. Is G1 motion service active?')
        else:
            self.get_logger().info('Odometry messages received: ' + str(self.msg_count))

    def publish_odom(self):
        if self.latest_state is None:
            return

        state = self.latest_state
        now = self.get_clock().now().to_msg()

        px = float(state.position[0])
        py = float(state.position[1])
        pz = float(state.position[2])

        vx = float(state.velocity[0])
        vy = float(state.velocity[1])
        vyaw = float(state.yaw_speed)

        # IMU quaternion: [w, x, y, z]
        qw = float(state.imu_state.quaternion[0])
        qx = float(state.imu_state.quaternion[1])
        qy = float(state.imu_state.quaternion[2])
        qz = float(state.imu_state.quaternion[3])

        # --- TF: odom -> pelvis ---
        tf = TransformStamped()
        tf.header.stamp = now
        tf.header.frame_id = self.odom_frame
        tf.child_frame_id = self.base_frame
        tf.transform.translation.x = px
        tf.transform.translation.y = py
        tf.transform.translation.z = 0.0  # 2D nav, keep robot on ground plane
        tf.transform.rotation.x = qx
        tf.transform.rotation.y = qy
        tf.transform.rotation.z = qz
        tf.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(tf)

        # --- /odom ---
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = px
        odom.pose.pose.position.y = py
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        odom.pose.covariance[0] = 0.01
        odom.pose.covariance[7] = 0.01
        odom.pose.covariance[35] = 0.05

        odom.twist.twist.linear.x = vx
        odom.twist.twist.linear.y = vy
        odom.twist.twist.angular.z = vyaw

        odom.twist.covariance[0] = 0.01
        odom.twist.covariance[7] = 0.01
        odom.twist.covariance[35] = 0.05

        self.odom_pub.publish(odom)


def main(args=None):
    net_interface = 'enp5s0'
    if len(sys.argv) > 1:
        net_interface = sys.argv[1]

    print('[G1 Odom] Initializing Unitree DDS on interface: ' + net_interface)
    ChannelFactoryInitialize(0, net_interface)

    rclpy.init(args=args)

    node = G1OdomPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
