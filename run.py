#!/usr/bin/env python

import config.config as cfg
import gzip
import os
import sys
from glob import glob
from parsers.arxiv import ArxivParser
from serializers.serializer_mp import ArxivToMasterPipeline

def get_arguments():

    import argparse

    parser=argparse.ArgumentParser(description='Command line options.')

    parser.add_argument('-d',
                        '--diagnose',
                        dest = 'diag',
                        action = 'store_true',
                        help = 'Send one test ArXiv record to the pipeline')

    parser.add_argument('-r',
                        '--records',
                        dest = 'reclist',
                        action = 'store',
                        help = 'Name of file with records to be parsed')

    parser.add_argument('-c',
                        '--caldate',
                        dest = 'caldate',
                        action = 'store',
                        help = 'Process arXiv abstract metadata for YYYY-MM-DD')

    parser.add_argument('-a',
                        '--absdir',
                        dest = 'absdir',
                        action = 'store',
                        help = 'Name of directory holding incoming records')

    parser.add_argument('-p',
                        '--parse-only',
                        dest = 'parse_only',
                        action = 'store_true',
                        help = 'Parse record(s) but only return dictionary')

    args=parser.parse_args()
    return args



def main():

    args = get_arguments()

    parsed_records = []

    arxiv = ArxivParser()


    print ("\n\nBEGIN find records to parse ...")
    if args.caldate:
        file_pattern=args.caldate
        glob_pattern=cfg.UPDATE_AGENT_DIR+'/*'+file_pattern+'*'
        try:
            infile=glob(glob_pattern)[0]
        except IndexError:
            print "No file found for that date."
        else:
            args.reclist = '@'+infile


    if args.diag:
        reclist = ['config/1111.0262']

    elif args.reclist:
        reclist=args.reclist.split(',')
        if reclist[0][0] == '@':
            infile = reclist[0][1:]
            reclist = []
            if '.gz' in infile:
                fp = gzip.open(infile, 'r')
                for l in fp.readlines():
                    reclist.append(cfg.INCOMING_ABS_DIR+'/'+l.split()[0])
                fp.close()
            else:
                with open(infile, 'rU') as fp:
                    reclist.append(fp.readlines().split()[0])
        else:
            reclist = map(lambda x: cfg.ARCHIVE_ABS_DIR + '/' + x.replace('.','/'), reclist)
            print (reclist)
    elif args.absdir:
        reclist = glob(args.absdir+'/*')
    else:
        print 'Empty record list.'
        reclist = []


    if (len(reclist) > 0):
        print "\n\nBEGIN parse reclist ...\n\n"
        for f in reclist:
            with open(f,'rU') as fp:
                parsed_records.append(arxiv.parse(fp))

        print "\n\nBEGIN send parsed records to Master Pipeline ...\n\n"
        for r in parsed_records:
            if args.parse_only:
                print ("\n"+str(r)+"\n")
            else:
                mpsender=ArxivToMasterPipeline()
                mpsender.serialize(r)

    print "DONE."
    return


if __name__ == '__main__':
    main()
