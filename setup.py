"""setup file for pip packaging and deployment"""
from subprocess import Popen, PIPE

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    LONG_DESCRIPTION = ""


with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()

import sys
def python_2_and_3_compatible(object):
    """to decide what type to return based on what is running"""
    if sys.version_info[0] < 3:
        text_type = unicode
    else:
        text_type = str
    if isinstance(object, text_type):
        result = object.encode('utf-8')
    else:
        result = object
    return result

def get_git_version(default="v0.0.1"):
    """runs the command to get the local version of git"""
    try:
        _p = Popen(['git', 'describe', '--tags'], stdout=PIPE, stderr=PIPE)
        _p.stderr.close()
        line = _p.stdout.readlines()[0]
        line = line.strip()
        if isinstance(default, unicode):
            return python_2_and_3_compatible(line)
    except Exception:
        return default


setup(
    name='pyingest',
    version=get_git_version(default="v0.0.1"),
    url='https://github.com/adsabs/adsabs-pyingest',
    license='MIT',
    author="NASA/SAO ADS",
    author_email="ads@cfa.harvard.edu",
    description='ADS collection or python parsers, validators, and \
                 serializers for adsabs ingest pipeline',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=REQUIRED
)
