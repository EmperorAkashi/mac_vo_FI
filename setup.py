from setuptools import setup, find_packages
import os

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    
# Filter out comments and empty lines
requirements = [r for r in requirements if r and not r.startswith('#')]

# Add all directories as packages, even if they don't have __init__.py files
packages = find_packages()
# Add top-level directories as packages
for item in os.listdir('.'):
    if os.path.isdir(item) and not item.startswith('.') and not item in ['__pycache__', 'asset', 'Docker', 'Scripts']:
        packages.append(item)

py_modules = ["MACVO"]  # Include the main MACVO.py file as a module

setup(
    name="macvo",
    version="0.1.0",
    packages=packages,
    py_modules=py_modules,  # Include standalone Python files
    package_dir={},  # No special package directory mapping needed
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
