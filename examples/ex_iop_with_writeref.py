#!/usr/bin/env python

from __future__ import print_function
from pyingest.parsers.iop import IOPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter
from glob import glob
import json


outfile = 'iop_test.tag'

journal_ISSN = {
    '0004-637X': 'ApJ',
#   '2041-8205': 'ApJL',
#   '2515-5172': 'RNAAS',
#   '1538-3873': 'PASP',
    '0143-0807': 'EJPh'
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
            print(("Error in IOP parser:", p, e))

    # Write everything out in Classic tagged format
    fo = open(outfile, 'a')

    serializer = Tagged()
    ref_handler = ReferenceWriter()

    for d in documents:
        print(json.dumps(d, indent=4, sort_keys=True))
        print("\n\n\n\n\n")
        serializer.write(d, fo)
        try:
            ref_handler.writeref(d,'iop')
        except Exception as err:
            print(("Error with writeref:", err))
    fo.close()
