#!/usr/bin/env python

import os
from glob import glob
from parsers.arxiv import ArxivParser


def main():
    testfiles= [x for x in glob('test/arxiv.test/*') if not os.path.isdir(x)]
    for f in testfiles:
        print f
        arxiv = ArxivParser()
        with open(f,'rU') as fp:
            x = arxiv.parse(fp)
            for k in x.keys():
                print "%s:\t%s"%(k,x[k])
    return


if __name__ == '__main__':
    main()
