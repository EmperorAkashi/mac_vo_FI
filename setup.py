from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    
# Filter out comments and empty lines
requirements = [r for r in requirements if r and not r.startswith('#')]

setup(
    name="macvo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.10",
    description="MAC-VO: Visual Odometry",
    author="MAC-VO Team",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
