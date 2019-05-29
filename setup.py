import os
import glob
from subprocess import Popen, PIPE

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ""

with open('requirements.txt') as f:
    required = f.read().splitlines()

def get_git_version(default="v0.0.1"):
    try:
        p = Popen(['git', 'describe', '--tags'], stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        line = p.stdout.readlines()[0]
        line = line.strip()
        return line
    except:
        return default

setup(
    name='pyingest',
    version=get_git_version(default="v0.0.1"),
    url='https://github.com/adsabs/adsabs-pyingest',
    license='MIT',
    author="NASA/SAO ADS",
    author_email="ads@cfa.harvard.edu",
    description='ADS collection or python parsers, validators, and serializers for adsabs ingest pipeline',
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=required
  )
