from pyingest.parsers.aip import AIPJATSParser
from pyingest.serializers.classic import Tagged
import pyingest.config.config as config


infile = '/proj/ads/abstracts/data/AIP/AIP.test/RSI/v91/i5/054901_1/Markup/VOR_10.1063_5.0005676.xml'


#try:
with open(infile,'rU') as fp:
    lol = AIPJATSParser()
    doc = lol.parse(fp)
    wut = Tagged()
    fo = open('lollol.lol','a')
    wut.write(doc,fo)
    fo.close()
#except Exception, err:
#    print "nope",err
