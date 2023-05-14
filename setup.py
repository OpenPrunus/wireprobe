#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='wireprobe',
      version='0.1.7',
      description='A wireguard probe',
      long_description="This package monitor wireguard client's tunnel if is up or down",
      author='Benjamin Gounine',
      author_email='prunus@ecuri.es',
      url='https://github.com/OpenPrunus/wireprobe/',
      python_requires='>3.9',
      install_requires=["decorator", "fabric", "invoke", "pyyaml", "urllib3"],
      packages=find_packages(where="fabfile"),
      package_dir={"": "fabfile"},
      include_package_data=True,
      )
