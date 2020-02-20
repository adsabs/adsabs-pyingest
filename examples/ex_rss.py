#!/usr/bin/env python
import os
import sys
from pyingest.parsers.default import BaseRSSFeedParser
from pyingest.serializers.classic import Tagged

rss_url = 'http://www.reddit.com/r/python/.rss'

parser = BaseRSSFeedParser()
documents = parser.parse(rss_url)

outputfp = open('rss.tag', 'a')
for d in documents:
    serializer = Tagged()
    serializer.write(d, outputfp)
outputfp.close()
