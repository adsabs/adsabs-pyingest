#!/usr/bin/env python

from __future__ import print_function
from pyingest.parsers.procsci import PoSParser
from pyingest.serializers.classic import Tagged

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Command line options:')
    parser.add_argument('-v',
                        '--volume',
                        dest='volume',
                        action='store',
                        help='PoS volume number (integer)')

    parser.add_argument('-o',
                        '--output',
                        dest='output',
                        action='store',
                        help='Output (tagged) file name')

    args = parser.parse_args()
    return args


def main():

    args = get_args()
    if args.volume:
        url = 'https://pos.sissa.it/' + args.volume

        parser = PoSParser()
        documents = parser.parse(url)

        if documents:
            if args.output:
                outfile = args.output
            else:
                outfile = 'PoS.' + args.volume + '.tag'
            outputfp = open(outfile, 'a')
            for d in documents:
                serializer = Tagged()
                serializer.write(d, outputfp)
            outputfp.close()
        else:
            print('No data extracted from pos.sissa.it.')
    else:
        print('You must provide a volume number, using -v ###')


if __name__ == '__main__':
    main()
