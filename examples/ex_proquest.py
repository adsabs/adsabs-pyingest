from __future__ import print_function
from glob import glob
from pyingest.parsers.proquest import ProQuestParser
from pyingest.serializers.classic import Tagged
from namedentities import *


def main():

    marc_filename = 'SAO_NASA_Jul_2020.UNX'
    oa_filename = marc_filename.replace('.UNX', '_OpenAccessTitles.csv')
    marcdata = open(marc_filename).read()
    oadata = open(oa_filename).read()
    parser = ProQuestParser(marcdata, oadata)
    lol = parser.parse()
    print("%s records processed" % len(parser.results))
    tag = Tagged()
    outfile = 'lolproque.tag'
    with open(outfile,'w') as fo:
        for rec in parser.results:
            tag.write(rec,fo)


if __name__ == '__main__':
    main()
