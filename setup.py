from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pbapi',
      version=version,
      description="This is the python pinboard API module",
      long_description="""\
      This module originally authored by Paul Mucur.   It was later developed by Morgan Craft.
      This module allows for an API interface with pinboard.in a popular bookmarking website. 
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
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
