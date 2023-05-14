#!/usr/bin/env python

from setuptools import setup

setup(name='wireprobe',
      version='0.1.2',
      description='A wireguard probe',
      author='Benjamin Gounine',
      author_email='prunus@ecuri.es',
      url='https://github.com/OpenPrunus/wireprobe/',
      python_requires='>3.9',
      install_requires=["decorator", "fabric", "invoke", "pyyaml", "urllib3"],
      )
