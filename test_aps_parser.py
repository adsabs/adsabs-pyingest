import glob
import cStringIO
import pyingest.parsers.aps as aps
import pyingest.serializers.classic
import traceback
import json
import xmltodict

#inline-formula in abstract:
#testfile = ['test_data/stubdata/input/apsjats_10.1103.PhysRevB.96.081117.fulltext.xml']

#generic testfile
#testfile = ['test_data/stubdata/input/apsjats_10.1103.PhysRevA.97.043801.fulltext.xml']

#multiple testfiles
testfile = glob.glob('test_data/stubdata/input/apsjats*')

#daily payload:
#testfile = list()
#logfile = '/proj/ads/abstracts/sources/APS/logs/aps-update.out.2018-05-08'
#with open(logfile,'rU') as fpp:
#    for l in fpp.readlines():
#        foo,bar,baz = l.split('\t')
#        testfile.append(bar)
#
##print("There are %s files.\n\n\n"%len(testfile))
#     
#testfile = [testfile[1]]

for f in testfile:
#   try:
    with open(f,'rU') as fp:
        parser = aps.APSJATSParser()
        document = parser.parse(fp)
#       print(document)
#       for k in document.keys():
#           print k,type(document[k])

        serializer = pyingest.serializers.classic.Tagged()
        outputfp = open('aps.tag','a')
        serializer.write(document,outputfp)
        outputfp.close()
#   except: 
#       print "ERROR!\n%s\n"%f
#       traceback.print_exc()
#       pass
#   else:
#       pass
#       print "OK:",f
