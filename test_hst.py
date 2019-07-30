#!/usr/bin/env python
import os
import sys
from pyingest.parsers.hstprop import HSTParser
from pyingest.serializers.classic import Tagged

try:
    token = os.environ['hst_token']
except KeyError:
    sys.exit("Please set API key in environment")

api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query'

parser = HSTParser()
documents = parser.parse(api_url, api_key=token, fromDate = '2019-01-01', maxRecords = 1)
outputfp = open('hstprop.tag','a')
for d in documents:
    serializer = Tagged()
    serializer.write(d,outputfp)
outputfp.close()
