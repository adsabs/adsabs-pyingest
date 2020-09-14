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


def get_git_version(default="v0.0.1"):
    """runs the command to get the local version of git"""
    try:
        _p = Popen(['git', 'describe', '--tags'], stdout=PIPE, stderr=PIPE)
        _p.stderr.close()
        line = _p.stdout.readlines()[0]
        line = line.strip()
        return line
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
