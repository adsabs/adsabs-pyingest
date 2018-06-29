
#!/usr/bin/env python

from argparse import ArgumentParser
import urllib
from pyingest.parsers.procsci import PoSParser
import pyingest.serializers.classic


parser = PoSParser()
documents = parser.parse('https://pos.sissa.it/299')



for d in documents:
    serializer = pyingest.serializers.classic.Tagged()
    outputfp = open('aps.tag','a')
    serializer.write(d,outputfp)
    outputfp.close()
