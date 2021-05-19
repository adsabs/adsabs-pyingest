#!/usr/bin/env python

from __future__ import print_function
from pyingest.parsers.oup import OUPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter
from glob import glob
import sys
import subprocess
import argparse

# MNRAS_EDIR  = "/proj/ads/abstracts/data/MNRAS/EARLY/test/"
# MNRAS_DIR  = "/proj/ads/abstracts/data/MNRAS/493.1/"
# MNRASL_DIR  = "/proj/ads/abstracts/data/MNRASL/493.1/"
# PTEP_DIR  = "/proj/ads/abstracts/data/PTEP"
# PASJ_DIR  = "/proj/ads/abstracts/data/PASJ"
# GJI_DIR  = "/proj/ads/abstracts/data/GJI"

#try:
#    DIR = sys.argv[1]
#except IndexError:
#    print('missing argument: top level directory required')
#    sys.exit(1)

outfile = 'mnras.tag'

parser = OUPJATSParser()
# files = glob(DIR+'/TagTextFiles/*.xml')
documents = []
files = ['/proj/ads/abstracts/data/MNRAS/504.1/TagTextFiles/stab770.xml',
         '/proj/ads/abstracts/data/MNRAS/504.4/TagTextFiles/stab367.xml'
        ]

for f in files:
    try:
        with open(f,'r') as fp:
            doc = parser.parse(fp)
            documents.append(doc)
    except Exception as e:
        print("Error in OUP parser:", f, e)

# Write everything out in Classic tagged format
fo = open(outfile, 'a')

serializer = Tagged()
# ref_handler = ReferenceWriter()

for d in documents:
    try:
        serializer.write(d,fo)
    except:
        print('lol serializer fail')
#       print(d)
    # ref_handler.writeref(d,'oup')
fo.close()


