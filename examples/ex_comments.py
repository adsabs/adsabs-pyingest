#!/usr/bin/env python

from __future__ import print_function
from pyingest.parsers.rnaas import RNAASJATSParser
from pyingest.serializers.classic import Tagged
from glob import glob

# parser = RNAASJATSParser()
# with open('/proj/ads/articles/sources/STACKS/2515-5172/3/7/95/rnaas_3_7_95.xml','rU') as fp:
#     documents = parser.parse(fp)
#
# outputfp = open('pos.tag','a')
# serializer = Tagged()
# serializer.write(documents,outputfp)
# outputfp.close()


parser = RNAASJATSParser()
# basedir = '/proj/ads/articles/sources/STACKS/2515-5172/3/7/'
# basedir = '/proj/ads/articles/sources/STACKS/0004-637X/878/1/'
# papers = glob(basedir+'*/*.xml')
papers = ['./apj_878_1_11.xml']
# papers = ['./rnaas_3_7_92.xml']
documents = []
for p in papers:
    print(("FILE:", p))
    # try:
    with open(p, 'rU') as fp:
        doc = parser.parse(fp)
    documents.append(doc)
    # except Exception as e:
    #     print "OH NOES:",e

fo = open('apj878.tag', 'a')
serializer = Tagged()
for d in documents:
    serializer.write(d, fo)
fo.close()
