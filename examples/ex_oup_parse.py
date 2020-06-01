#!/usr/bin/env python

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

try:
  DIR = sys.argv[1]
except IndexError:
  print 'missing argument: top level directory required'
  sys.exit(1)

outfile = 'oup.tag'

parser = OUPJATSParser()
files = glob(DIR+'/TagTextFiles/*.xml')
documents = []

for f in files:
    try:
        with open(f,'rU') as fp:
            doc = parser.parse(fp)
            documents.append(doc)
    except Exception as e:
        print("Error in OUP parser:", f, e)
#   print(documents) 

# Write everything out in Classic tagged format
fo = open(outfile, 'a')

serializer = Tagged()
ref_handler = ReferenceWriter()

for d in documents:
#   print(d)
    serializer.write(d,fo)
    ref_handler.writeref(d,'oup')
fo.close()


