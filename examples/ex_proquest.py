from __future__ import print_function
from glob import glob
from pyingest.parsers.proquest import ProQuestParser
from pyingest.serializers.classic import Tagged
from namedentities import *


def main():

    input_file = 'SAO_NASA_Jul_2020.UNX'
    parser = ProQuestParser(input_file)
    lol = parser.parse()
    print("%s records processed" % len(parser.results))
    tag = Tagged()
    outfile = 'lolproque.tag'
    with open(outfile,'w') as fo:
        for rec in parser.results:
            tag.write(rec,fo)

if __name__ == '__main__':
    main()
