from __future__ import print_function
import os
from glob import glob
from pyingest.parsers.proquest import ProQuestParser
from pyingest.serializers.classic import Tagged
from namedentities import *


def main():

    marc_filename = '/Users/mtemple/Desktop/SAO_NASA_Feb_2024.UNX'
    oa_filename = marc_filename.replace('.UNX', '_OpenAccessTitles.csv')
    marcdata = open(marc_filename).read()
    if os.path.exists(oa_filename):
        oadata = open(oa_filename).read()
    else:
        oadata = ''
    parser = ProQuestParser(marcdata, oadata)
    lol = parser.parse()
    print("%s records processed" % len(parser.results))
    tag = Tagged()
    outfile = marc_filename+'.NEW'
    with open(outfile,'w') as fo:
        for rec in parser.results:
            tag.write(rec,fo)


if __name__ == '__main__':
    main()
