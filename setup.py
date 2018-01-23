try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os


os.system('pip install --upgrade git+https://github.com/seasidesparrow/adsabs-pyingest.git@master')

setup(name='pyingest',
      version='0.5.0',
      packages=['pyingest']
#     install_requires=[
#           'jsonschema',
#           'namedentities',
#           'python-dateutil'
#     ],
  )
