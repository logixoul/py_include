# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='lib',  # Required
    version='1.0.0',  # Required
	description='A sample Python project',  # Required

    classifiers=[  # Optional
        'Programming Language :: Python :: 3.6',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=['pyqt5', 'numpy', 'scipy'],  # Optional
)