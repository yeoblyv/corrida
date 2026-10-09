import os
from glob import glob

from setuptools import find_packages, setup

package_name = "corrida_bringup"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Yehor Oblyvantsov",
    maintainer_email="xineraman8@gmail.com",
    description="Launch files and configuration that bring the Corrida robot stack up",
    license="MIT",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "odom_relay = corrida_bringup.odom_relay:main",
        ],
    },
)
