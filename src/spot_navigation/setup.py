from setuptools import setup
import os
from glob import glob
setup(
    name='spot_navigation',
    version='1.0.0',
    packages=['spot_navigation'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/spot_navigation']),
        ('share/spot_navigation', ['package.xml']),
        (os.path.join('share', 'spot_navigation', 'worlds'), glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Aman Jaiswal',
    maintainer_email='aerraj50@gmail.com',
    description='Spot Navigation - Tech Zephyr 3.0',
    license='MIT',
    entry_points={'console_scripts': ['spot_navigator = spot_navigation.spot_sequential_navigator:main']},
)
