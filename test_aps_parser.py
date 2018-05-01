import glob
import cStringIO
import pyingest.parsers.aps as aps
import pyingest.serializers.classic
import traceback
import json
import xmltodict

#funky inline-formal in abstract:
#testfile = ['test_data/stubdata/input/apsjats_10.1103.PhysRevB.96.081117.fulltext.xml']

#generic testfile
#testfile = ['test_data/stubdata/input/apsjats_10.1103.PhysRevA.97.043801.fulltext.xml']

#multiple testfiles
#testfile = glob.glob('test_data/stubdata/input/apsjats*')

#daily payload:
testfile = list()
logfile = '/proj/ads/abstracts/sources/APS/logs/aps-update.out.2018-03-05'
with open(logfile,'rU') as fpp:
    for l in fpp.readlines():
        foo,bar,baz = l.split('\t')
        testfile.append(bar)

#print("There are %s files.\n\n\n"%len(testfile))
     

for f in testfile:
    try:
        with open(f,'rU') as fp:
            lol = fp.read()
            fp.seek(0)
            parser = aps.APSJATSParser()
            document = parser.parse(fp)

            serializer = pyingest.serializers.classic.Tagged()
            outputfp = open('aps.tag','a')
            serializer.write(document,outputfp)
            outputfp.close()
    except: 
        print "ERROR!\n%s\n"%f
#       print(json.dumps(xmltodict.parse(lol),sort_keys=True,indent=1))
        traceback.print_exc()
    else:
        print "OK:",f
