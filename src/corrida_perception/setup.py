from setuptools import find_packages, setup

package_name = "corrida_perception"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="daniel",
    maintainer_email="nwadikedaniel6@gmail.com",
    description="Perception components for the Corrida maze robot",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "bumper = corrida_perception.bumper:main",
        ],
    },
)
