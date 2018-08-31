#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup


setup(name='dismock',
      version='1.0.0',
      description='Automate the testing of discord bots',
      url='http://github.com/DXsmiley/dismock',
      author='DXsmiley, Doezer',
      license='MIT',
      packages=['dismock'],
      install_requires=['discord.py'],
      dependency_links=['git+ssh://git@github.com/Rapptz/discord.py@rewrite#egg=discord.py'],
      zip_safe=False
)
