from pyingest.parsers.aip import AIPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter
import pyingest.config.config as config


# infile = '/proj/ads/abstracts/data/AIP/AIP.test/RSI/v91/i5/054901_1/Markup/VOR_10.1063_5.0005676.xml'
# infile = '/proj/ads/abstracts/data/AIP/JATS.0127/JCP/v154/i2/024904_1/Markup/VOR_10.1063_5.0033645.xml'
# infile = '/proj/ads/abstracts/data/AIP/JATS.0127/AJP/v89/i2/210_1/Markup/VOR_10.1119_10.0002365.xml'
infile = '/Users/mtempleton/VOR_10.1063_5.0052678.xml'


with open(infile,'r') as fp:
    lol = AIPJATSParser()
    doc = lol.parse(fp)
    # print("Hi, ... %s" % doc)
    wut = Tagged()
    with open('lollol.lol','a') as fo:
        wut.write(doc,fo)
    foo = ReferenceWriter()
    foo.topdir = './'
    # try:
    foo.writeref(doc,'aip')
    # except Exception as err:
        # print("Error with writeref:", err)
