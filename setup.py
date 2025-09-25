from setuptools import setup, find_packages
import pathlib

# Get the current directory
here = pathlib.Path(__file__).parent.resolve()

# Read the requirements from requirements.txt
with open(here / 'requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    packages=find_packages(where='src'),  
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires='>=3.11',
)
