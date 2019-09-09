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
# RNAAS test:
#basedir = '/proj/ads/articles/sources/STACKS/2515-5172/3/7/'

# ApJ test:
#basedir = '/proj/ads/articles/sources/STACKS/0004-637X/878/1/'

parser = IOPJATSParser()

basedir = '/proj/ads/articles/sources/STACKS/'


for issn in journal_ISSN.keys():
    b2 = basedir+issn
    vols = glob(b2+'/*')
    v = vols[-1]
    papers = glob(v+'/*/*/*.xml')
#papers = []
#with open('iop.bad','rU') as fb:
#    for ff in fb.readlines():
#        papers.append(ff.strip())
        
    # Try the parser

    documents = []
    for p in papers:
        print "file:",p
        try:
            with open(p,'rU') as fp:
                doc = parser.parse(fp)
            documents.append(doc)
        except Exception as e:
            print "Error in IOP parser:",p,e
        print "\n\n\n"


    # Write everything out in Classic tagged format
    fo = open(outfile,'a')

    serializer = Tagged()

    for d in documents:
        if 'references' in d:
            del(d['references'])
#       else:
#           print("References have been stripped!")
        serializer.write(d,fo)
    fo.close()
