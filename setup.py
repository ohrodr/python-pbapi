from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pbapi',
      version=version,
      description="This is a python OO pinboard API module",
      long_description="""\
      This module allows for interfacing with the pinboard API for http://pinboard.in a social bookmarking website. 
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Robb Driscoll',
      author_email='ohrodr@gmail.com',
      url='http://odr.me',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests',]),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'simplejson' 
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
