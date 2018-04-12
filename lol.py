import glob
import cStringIO
import pyingest.parsers.aps as aps
import pyingest.serializers.classic

#testfile = 'test_data/stubdata/input/apsjats_10.1103.PhysRevA.97.043801.fulltext.xml'
testfile = glob.glob('test_data/stubdata/input/apsjats*')
for f in testfile:
    with open(f,'rU') as fp:
        parser = aps.APSJATSParser()
        document = parser.parse(fp)

#   print(document.keys())

#serializer = pyingest.serializers.classic.Tagged()
#outputfp = open('lolbutts.tag','w')
#serializer.write(document,outputfp)
#outputfp.close()

#with open('lel.txt','w') as fp:
#    fp.write(output)
#outputfp.close()
