#!/usr/bin/env python

from __future__ import print_function
from pyingest.parsers.iop import IOPJATSParser
from pyingest.serializers.classic import Tagged
from glob import glob
import json


outfile = 'iop_test.tag'

journal_ISSN = {
    '1538-4357': 'ApJL',
}

parser = IOPJATSParser()

basedir = '/proj/ads/articles/sources/STACKS/'

for issn in journal_ISSN.keys():
    b2 = basedir + issn
    vols = glob(b2 + '/*')
    v = vols[-1]
    papers = glob(v + '/*/*/*.xml')

    # Try the parser
    documents = []
    for p in papers:
        try:
            with open(p, 'rU') as fp:
                doc = parser.parse(fp)
            documents.append(doc)
        except Exception as e:
            print("Error in IOP parser:", p, e)

    # Write everything out in Classic tagged format
    fo = open(outfile, 'a')

    serializer = Tagged()

    for d in documents:
        print("KEYS:", list(d.keys()))
        print(json.dumps(d, indent=4, sort_keys=True))
        # print("Hi, here's a document structure:\n%s\n\n\n"%d)
        # serializer.write(d, fo)
    fo.close()
