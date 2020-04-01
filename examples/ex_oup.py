#!/usr/bin/env python

from pyingest.parsers.oup import OUPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter
from glob import glob
import argparse

INPUT_DIR  = "/proj/ads/abstracts/data/MNRAS/493.1/TagTextFiles"

outfile = 'oup.tag'

documents = []
parser = OUPJATSParser()

files = glob(INPUT_DIR+'/*.xml')

print("I found %d files to process" % len(files))

for f in files:
    try:
        with open(f,'rU') as fp:
            doc = parser.parse(fp)
            documents.append(doc)
    except Exception as e:
        print("Error in OUP parser:", f, e)


# Write everything out in Classic tagged format
fo = open(outfile, 'a')

serializer = Tagged()
# ref_handler = ReferenceWriter()

for d in documents:
    serializer.write(d,fo)
    # ref_handler.writeref(d)
fo.close()


