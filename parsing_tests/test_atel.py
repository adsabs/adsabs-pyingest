#!/usr/bin/env python
import os
import sys
from pyingest.parsers.atel import ATelParser
from pyingest.serializers.classic import Tagged

rss_url = 'http://www.astronomerstelegram.org/?adsbiblio'

parser = ATelParser()
documents = parser.parse(rss_url, data_tag='item')

outputfp = open('atel.tag','a')
for d in documents:
    serializer = Tagged()
    serializer.write(d,outputfp)

outputfp.close()

