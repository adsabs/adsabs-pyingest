#!/usr/bin/env python

from pyingest.parsers.oup import OUPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter
from glob import glob
import subprocess
import argparse

MNRAS_EDIR  = "/proj/ads/abstracts/data/MNRAS/EARLY/test/"
MNRAS_DIR  = "/proj/ads/abstracts/data/MNRAS/493.1/"
MNRASL_DIR  = "/proj/ads/abstracts/data/MNRASL/493.1/"
PTEP_DIR  = "/proj/ads/abstracts/data/PTEP"
PASJ_DIR  = "/proj/ads/abstracts/data/PASJ"
GJI_DIR  = "/proj/ads/abstracts/data/GJI"

outfile = 'oup.tag'

documents = []
parser = OUPJATSParser()

#for file in sys.argv[1:]:
#d = None
#with open(file, 'r') as fp:
#print p.parse(fp)
#d = p.parse(fp)
#print json.dumps(d, indent=2)

#files = ['/proj/ads/abstracts/data/MNRAS/493.1/TagTextFiles/staa269.xml',
#           '/proj/ads_abstracts/data/MNRAS/488.2/TagTextFiles/stz1191.xml',
#           '/proj/ads_abstracts/data/MNRAS/488.1/TagTextFiles/stz1253.xml',
#             '/proj/ads/abstracts/data/MNRAS/488.1/TagTextFiles/stz1626.xml',
#             '/proj/ads/abstracts/data/MNRAS/EARLY/test/staa698.xml']


files = glob(MNRAS_EDIR+'*/*.xml')

for f in files:
    # try:
        with open(f,'rU') as fp:
            doc = parser.parse(fp)
            documents.append(doc)
    # except Exception as e:
        # print("Error in OUP parser:", f, e)
#   print(documents) 

# Write everything out in Classic tagged format
fo = open(outfile, 'a')

serializer = Tagged()
ref_handler = ReferenceWriter()

for d in documents:
#   print(d)
    serializer.write(d,fo)
    ref_handler.writeref(d)
fo.close()


