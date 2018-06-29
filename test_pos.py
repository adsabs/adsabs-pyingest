#!/usr/bin/env python

from pyingest.parsers.procsci import PoSParser
from pyingest.serializers.classic import Tagged

parser = PoSParser()
documents = parser.parse('https://pos.sissa.it/288')

outputfp = open('pos.tag','a')
for d in documents:
    serializer = Tagged()
    serializer.write(d,outputfp)
outputfp.close()
