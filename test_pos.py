import pyingest.parsers.ProcSci as pos
import pyingest.serializers.classic
import traceback

url = 'https://pos.sissa.it/295/'

try:
    parser = pos.PoSParser()
    document = parser.parse(url)

    for d in document:
        serializer = pyingest.serializers.classic.Tagged()
        outputfp = open('PoS.tag','a')
        serializer.write(d,outputfp)
        outputfp.close()
except: 
    print "ERROR!\n"
    traceback.print_exc()
else:
    pass
