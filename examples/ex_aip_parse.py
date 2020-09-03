#!/usr/bin/env python

from pyingest.parsers.aip import AIPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter
from glob import glob
import sys
import subprocess
import argparse

try:
  DIR = sys.argv[1]
except IndexError:
  print 'missing argument: top level directory required'
  sys.exit(1)

outfile = 'aip.tag'

parser = AIPJATSParser()
files = glob(DIR+'/*/*/*/*/*/*.xml')
documents = []

for f in files:
    try:
        with open(f,'rU') as fp:
            doc = parser.parse(fp)
            documents.append(doc)
    except Exception as e:
        print("Error in AIP parser:", f, e)
#   print(documents) 

# Write everything out in Classic tagged format
fo = open(outfile, 'a')

serializer = Tagged()
ref_handler = ReferenceWriter()

for d in documents:
#   print(d)
    serializer.write(d,fo)
    ref_handler.writeref(d,'aip')
fo.close()


