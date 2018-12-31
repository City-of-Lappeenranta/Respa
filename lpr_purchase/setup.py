import os
import re
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='lpr_purchase',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
)
