"""G1 Navigation bringup launch file."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('g1_nav')
    urdf_path = os.path.join(pkg_share, 'urdf', 'g1.urdf')

    # Use Nav2's default RViz config (has all Nav2 tools/displays preconfigured)
    rviz_config = '/opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz'

    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    interface_arg = DeclareLaunchArgument(
        'interface', default_value='enp5s0',
        description='Network interface for Unitree SDK'
    )

    # Robot state publisher - publishes TF from URDF
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}],
    )

    # Joint publisher - real joints from G1 via Unitree SDK (uses parameter)
    joint_publisher = Node(
        package='g1_nav',
        executable='joint_publisher',
        name='joint_publisher',
        output='screen',
        parameters=[{'interface': LaunchConfiguration('interface')}],
    )

    # Robot connector - bridges ROS2 cmd_vel to G1 (uses parameter)
    robot_connector = Node(
        package='g1_nav',
        executable='robot_connector',
        name='robot_connector',
        output='screen',
        parameters=[{'interface': LaunchConfiguration('interface')}],
    )

    # Odom publisher - reads G1's rt/odommodestate via Unitree SDK (uses argv)
    odom_publisher = Node(
        package='g1_nav',
        executable='odom_publisher',
        name='odom_publisher',
        output='screen',
        arguments=[LaunchConfiguration('interface')],
    )

    # Static TF: mid360_link -> livox_frame (LiDAR is inverted, 180 roll)
    mid360_to_livox = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='mid360_to_livox',
        arguments=['0', '0', '0', '0', '0', '3.14159265', 'mid360_link', 'livox_frame'],
    )

    # PointCloud to LaserScan converter
    pointcloud_to_laserscan = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        remappings=[
            ('cloud_in', '/livox/lidar'),
            ('scan', '/scan'),
        ],
        parameters=[{
            'target_frame': 'pelvis',
            'transform_tolerance': 0.01,
            'min_height': -0.3,
            'max_height': 1.5,
            'angle_min': -3.14159,
            'angle_max': 3.14159,
            'angle_increment': 0.0087,
            'scan_time': 0.1,
            'range_min': 0.3,
            'range_max': 30.0,
            'use_inf': True,
        }],
        output='screen',
    )

    # RViz with Nav2 default config
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
    )

    return LaunchDescription([
        interface_arg,
        robot_state_publisher,
        joint_publisher,
        robot_connector,
        odom_publisher,
        mid360_to_livox,
        pointcloud_to_laserscan,
        rviz,
    ])
