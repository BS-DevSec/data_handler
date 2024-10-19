# setup.py

from setuptools import setup, find_packages

setup(
    name='data_handler',  # Replace with your desired package name
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'matplotlib',
        'seaborn',
        'PyYAML',
        'pytest',
        'pytest-cov',
        'pytest-mock',
        # Add other dependencies as needed
    ],
)
