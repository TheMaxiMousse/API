"""
Package setup script for the API.
This script is used to package the API application for distribution.
It reads the Python version from the Dockerfile and the application version from the main module.
It also reads the requirements from a requirements.txt file and sets up the package metadata.
"""

from setuptools import find_packages, setup


# Read the Python version from Dockerfile
def get_python_version():
    """Retrieve the Python version from the Dockerfile."""
    with open("Dockerfile", encoding="utf-8") as f:
        for line in f:
            if line.startswith("FROM python:"):
                return line.split(":")[1].split("-")[0].strip()
    raise RuntimeError("Version not found.")


# Read the app version from the main module
def get_app_version():
    """Retrieve the application version from the main module."""
    with open("app/main.py", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise RuntimeError("App version not found in app.main module.")


def get_requirements():
    """Retrieve the requirements from the requirements.txt file."""
    with open("requirements.txt", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="chocomax-api",
    version=get_app_version(),
    url="https://github.com/TheChocoMax/API",
    description="ChocoMax API",
    author="Vianpyro",
    packages=find_packages(where="app", exclude=["tests*"]),
    package_dir={"": "app"},
    include_package_data=True,
    install_requires=get_requirements(),
    python_requires=f">={get_python_version()}",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "chocomax-api=main:main",
        ],
    },
)
