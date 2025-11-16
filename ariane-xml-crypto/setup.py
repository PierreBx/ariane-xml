"""
Setup script for Ariane-XML Encryption Module.
"""

from setuptools import setup

setup(
    name='ariane-xml-crypto',
    version='1.0.0',
    description='Encryption and pseudonymization module for Ariane-XML XML data',
    author='Ariane-XML Team',
    packages=['ariane_xml_crypto'],
    package_dir={'ariane_xml_crypto': '.'},
    install_requires=[
        'cryptography>=41.0.0',
        'pyyaml>=6.0',
        'faker>=19.0.0',
        'lxml>=4.9.0',
        'ff3>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'ariane-xml-encrypt=ariane_xml_crypto.cli:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
