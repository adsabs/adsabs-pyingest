from __future__ import print_function
import os
import glob
import pyingest.parsers.aps as aps
import pyingest.parsers.arxiv as arxiv
import pyingest.serializers.classic
import traceback
import json
import xmltodict
from datetime import datetime

input_list = 'bibc.2.out'
testfile=[]
xmldir = '/proj/ads/fulltext/sources/downloads/cache/APS_HARVEST/harvest.aps.org/v2/journals/articles/'
xmltail = '/fulltext.xml'
with open(input_list,'rU') as fi:
    for l in fi.readlines():
        doi = l.strip().split('\t')[1]
        (a,b) = doi.split('/')
        b = b.replace('.','/')
        infile = xmldir + a + '/' + b + xmltail
        testfile.append(infile)

for f in testfile:
    fnord = f[92:]
    if os.path.isfile(f):
        print("found! ",fnord)
        with open(f, 'rU') as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
            serializer = pyingest.serializers.classic.Tagged()
            outputfp = open('aps.tag', 'a')
            serializer.write(document, outputfp)
            outputfp.close()
    #except:
    #    print "ERROR!\n%s\n"%f
    #    traceback.print_exc()
    #    pass
    else:
        print("not found :(   ", fnord)
