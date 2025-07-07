from setuptools import setup, find_packages
import os

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    
# Filter out comments and empty lines
requirements = [r for r in requirements if r and not r.startswith('#')]

# Find all packages in the repository
packages = find_packages()

# Make sure we include all directories that contain Python files
package_dir = {}
py_modules = ["MACVO"]  # Include the main MACVO.py file as a module

setup(
    name="macvo",
    version="0.1.0",
    packages=packages,
    py_modules=py_modules,  # Include standalone Python files
    package_dir=package_dir,
    install_requires=requirements,
    python_requires=">=3.10",
    description="MAC-VO: Visual Odometry",
    author="MAC-VO Team",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
