from setuptools import setup
import os

# no github commands in install requires, will require an official release.
os.system('pip install --upgrade git+https://github.com/adsabs/ADSPipelineUtils.git')

setup(
    name='pyingest',
    version='0.5.0',
    packages=['pyingest','pyingest.config','pyingest.extractors','pyingest.parsers','pyingest.serializers','pyingest.validators','pyingest.extractors.grobid'],
    install_requires=['bs4<=0.0.1', 'lxml<=4.2.1', 'functools32<=3.2.3.post2', 'jsonschema<=2.6.0', 'namedentities<=1.9.4', 'python-dateutil<=2.6.0', 'six<=1.11.0', 'xmltodict<=0.11.0']
)
