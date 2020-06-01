'''
This example will harvest everything currently available via the PNAS RSS
feeds and put it into a single output file called pnas.tag
'''
import feedparser
import requests
from pyingest.parsers.pnas import PNASParser
from pyingest.serializers.classic import Tagged

PNAS_RSS_URLS = {
    'astronomy':'http://www.pnas.org/rss/Astronomy.xml',
    'planetary':'http://www.pnas.org/rss/Earth,_Atmospheric,_and_Planetary_Sciences.xml',
    'apphyssci':'http://www.pnas.org/rss/Applied_Physical_Sciences.xml',
    'engineer':'http://www.pnas.org/rss/Engineering.xml',
    'environm':'http://www.pnas.org/rss/Environmental_Sciences.xml',
    'geology':'http://www.pnas.org/rss/Geology.xml',
    'geophys':'http://www.pnas.org/rss/Geophysics.xml',
    'physics':'http://www.pnas.org/rss/Physics.xml'
}

basedir = '/proj/ads/abstracts/sources/PNAS'

outfile = 'pnas.tag'
fo = open(outfile,'a')

for k, v in PNAS_RSS_URLS.items():
    feed = feedparser.parse(v)
    print "feed:",k
    for _item in feed['entries']:
        try:
            record = {}
            absURL = _item['link']
            volno  = _item['prism_volume'].zfill(4)
            ident  = _item['dc_identifier']
            ident = ident.replace('hwp:master-id:pnas;','')
            print absURL,volno,ident
            pnas = PNASParser()
            output = pnas.parse(absURL)
        except Exception, err:
            print "Error in parser:",err
        else:
            try:
                serializer = Tagged()
                serializer.write(output,fo)
            except Exception, err:
                print "Error in serializer:",err
