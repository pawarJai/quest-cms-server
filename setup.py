# setup.py
from setuptools import setup, find_packages
from pathlib import Path

HERE = Path(__file__).parent

# read README (optional)
readme = (HERE / "README.md").read_text(encoding="utf8") if (HERE / "README.md").exists() else ""

# Read requirements.txt if present
requirements = []
req_file = HERE / "requirements.txt"
if req_file.exists():
    requirements = [r.strip() for r in req_file.read_text().splitlines() if r.strip() and not r.startswith("#")]

setup(
    name="my-backend",                      # change to your preferred package name
    version="0.1.0",
    description="My backend server package",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests", "venv",)),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            # Creates 'run-backend' CLI that calls server.app.main:main
            "run-backend = app.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
