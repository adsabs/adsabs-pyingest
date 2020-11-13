from datetime import datetime
import feedparser
import os
import requests
import urllib
from config import *
from pyingest.parsers.pnas import PNASParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter

current_date = datetime.now()
year = str(current_date.year)
month= str(current_date.month)
day  = str(current_date.day)
batch = "%s%s%s" % (year,month.zfill(2),day.zfill(2))

outfile = PNAS_ARCHIVE_DIR + 'batch/' + batch + '.txt'

print("Begin PNAS harvest: %s" % str(current_date))
records = []
for k, v in PNAS_RSS_URLS.items():
    feed = feedparser.parse(v)
    category = k
    fw = open('pnas_feedparser.resp','w')
    fw.write(str(feed))
    fw.close()
    for _item in feed['entries']:
        try:
            record = {}
            absURL = _item['link']
            volno  = _item['prism_volume'].zfill(4)
            ident  = _item['dc_identifier']
            ident = ident.replace('hwp:master-id:pnas;','')
            archive_dir = PNAS_ARCHIVE_DIR + str(volno) + '/'

            if not os.path.exists(archive_dir):
                os.mkdir(archive_dir)

            archive_file = archive_dir + category + '_' + ident + '.html'

            # check archive: do we already have it?  If not, copy & parse it.
            if not os.path.exists(archive_file):
                abs_source = urllib.urlopen(absURL).read()
                open(archive_file, 'w').write(abs_source)
                pnas = PNASParser()
                output = pnas.parse(absURL)
                records.append(output)
        except Exception, err:
            print("Error parsing %s: %s:" % (absURL,err))

if records:
    try:
        fo = open(outfile,'a')
        for rec in records:
            try:
                serializer = Tagged()
                serializer.write(rec,fo)
            except Exception, err:
                print("Error in serializer: %s" % err)
            try:
                ref_handler = ReferenceWriter()
                ref_handler.writeref(rec,'pnas')
            except Exception, err:
                print("Error in writeref: %s" % err)
        print("New PNAS records available in %s" % outfile)
        fo.close()
    except:
        print("Error writing PNAS records: %s" % err)
else:
    print("No new PNAS records available.")

print("End PNAS harvest.")
