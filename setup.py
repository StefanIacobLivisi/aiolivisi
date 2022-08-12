"""Setup for aiolivisi."""
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

REQUIREMENTS = list(val.strip() for val in open("requirements.txt"))
MIN_PYTHON_VERSION = "3.8"

setup(
    name="aiolivisi",
    version="0.0.6",
    license="Apache License 2.0",
    author="Stefan Iacob",
    author_email="stefan.iacob.extern@livisi.de",
    description="Python module to communicate with LIVISI Smart Home Controllers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StefanIacobLivisi/aiolivisi",
    packages=find_packages(),
    platforms="any",
    install_requires=REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)