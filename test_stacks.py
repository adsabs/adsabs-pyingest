#!/usr/bin/env python

from pyingest.parsers.rnaas import RNAASJATSParser
from pyingest.serializers.classic import Tagged

parser = RNAASJATSParser()
with open('/proj/ads/articles/sources/STACKS/2515-5172/3/7/95/rnaas_3_7_95.xml','rU') as fp:
    documents = parser.parse(fp)

#documents['bibcode'] = u'1995astro.ph..1013H'
#print documents

outputfp = open('pos.tag','a')
serializer = Tagged()
serializer.write(documents,outputfp)
outputfp.close()
