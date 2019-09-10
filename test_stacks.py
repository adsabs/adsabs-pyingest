#!/usr/bin/env python

from pyingest.parsers.iop import IOPJATSParser
from pyingest.serializers.classic import Tagged
from glob import glob
import json


outfile = 'iop_test.tag'

journal_ISSN = {
               '1538-3881':'AJ',
               '0004-6256':'AJ',
               '1475-7516':'JCAP',
               '0004-637X':'ApJ',
               '1538-4357':'ApJ',
               '0067-0049':'ApJS',
               '2041-8205':'ApJ',
               '1538-4357': 'ApJL',
               '2041-8205': 'ApJL',
               '2515-5172': 'RNAAS'
               }

parser = IOPJATSParser()

basedir = '/proj/ads/articles/sources/STACKS/'

for issn in journal_ISSN.keys():
    b2 = basedir+issn
    vols = glob(b2+'/*')
    v = vols[-1]
    papers = glob(v+'/*/*/*.xml')
        
    # Try the parser
    documents = []
    for p in papers:
        try:
            with open(p,'rU') as fp:
                doc = parser.parse(fp)
            documents.append(doc)
        except Exception as e:
            print "Error in IOP parser:",p,e

    # Write everything out in Classic tagged format
    fo = open(outfile,'a')

    serializer = Tagged()

    for d in documents:
        # references not present in Classic parser
#       if 'references' in d:
#           del(d['references'])
        serializer.write(d,fo)
    fo.close()
