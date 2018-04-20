import glob
import cStringIO
import pyingest.parsers.aps as aps
import pyingest.serializers.classic
import traceback

#funky inline-forumal in abstract:
#testfile = ['test_data/stubdata/input/apsjats_10.1103.PhysRevB.96.081117.fulltext.xml']

#generic testfile
#testfile = ['test_data/stubdata/input/apsjats_10.1103.PhysRevA.97.043801.fulltext.xml']

#multiple testfiles
testfile = glob.glob('test_data/stubdata/input/apsjats*')
for f in testfile:
    try:
        with open(f,'rU') as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)

            serializer = pyingest.serializers.classic.Tagged()
            outputfp = open('aps.tag','a')
            serializer.write(document,outputfp)
            outputfp.close()
    except: 
        print "\n\nERROR!\n%s\n\n"%f
        traceback.print_exc()
