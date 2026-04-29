import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'g1_nav'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes/g1_meshes'), glob('meshes/g1_meshes/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gakash',
    maintainer_email='gakash@todo.todo',
    description='G1 Navigation stack',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_connector = g1_nav.robot_connector:main',
            'joint_publisher = g1_nav.joint_publisher:main',
            'mola_fixed = g1_nav.mola_fixed:main',
            'odom_publisher = g1_nav.odom_publisher:main',
        ],
    },
)
