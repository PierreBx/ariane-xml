#!/usr/bin/env python3
"""
Setup script for Ariane-XML Jupyter Kernel
"""

from setuptools import setup, find_packages
import os

# Get the directory where setup.py is located
setup_dir = os.path.dirname(os.path.abspath(__file__))

# Read version from package __init__.py in the same directory
version = {}
version_file = os.path.join(setup_dir, "__init__.py")
with open(version_file) as f:
    exec([line for line in f if line.startswith("__version__")][0], version)

# Read README from parent directory if available
readme_file = os.path.join(setup_dir, '..', 'README.md')
long_desc = ''
if os.path.exists(readme_file):
    with open(readme_file) as f:
        long_desc = f.read()

setup(
    name='ariane-xml-jupyter-kernel',
    version=version['__version__'],
    description='Jupyter kernel for Ariane-XML - SQL-like XML querying',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    author='Ariane-XML Contributors',
    url='https://github.com/PierreBx/Ariane-XML',
    packages=['ariane_xml_jupyter_kernel'],
    package_dir={'ariane_xml_jupyter_kernel': '.'},
    package_data={
        'ariane_xml_jupyter_kernel': ['kernelspec/kernel.json']
    },
    install_requires=[
        'ipykernel>=6.0.0',
        'jupyter-client>=7.0.0'
    ],
    python_requires='>=3.8',
    classifiers=[
        'Framework :: Jupyter',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    entry_points={
        'console_scripts': [
            'ariane-xml-jupyter-kernel-install=ariane_xml_jupyter_kernel.install:main',
        ],
    },
)
