#!/usr/bin/env python
import os
import sys
from pyingest.parsers.joss import JOSSParser
from pyingest.serializers.classic import Tagged

rss_url = 'https://joss.theoj.org/papers/published.atom'

parser = JOSSParser()
documents = parser.parse(rss_url, since='2019-07-10', page=1)

outputfp = open('joss.tag', 'a')
for d in documents:
    serializer = Tagged()
    serializer.write(d, outputfp)

outputfp.close()
