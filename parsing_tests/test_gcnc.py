from pyingest.parsers.gcncirc import GCNCParser
from pyingest.serializers.classic import Tagged
from namedentities import *

def main():

    # flist = ['25548.gcn3','23456.gcn3','23457.gcn3','23458.gcn3','25321.gcn3','9999.gcn3','98765.gcn3']
    flist = []
    with open('26_5','rU') as fi:
        for l in fi.readlines():
            fname = l.strip() + '.gcn3'
            flist.append(fname)

    basedir = '/Users/mtempleton/Projects/GCN_Parser/gcn3/'

    with open('output.tag','w') as fo:
        for f in flist:
            f2 = basedir + f
            try:
                with open(f2,'rU') as fg:
                    try:
                        d = fg.read()
                    except Exception, err:
                        d = ''
                        print f2
                        print "couldnt read it:",err
                try:
                    # d = namedentities.hex_entities(d)
                    d = repr(hex_entities(d))
                except Exception, err:
                    d = ''
                    print f2
                    print "Couldnt convert to hex:",err
                try:
                    x = GCNCParser(d)
                except Exception, err:
                    print "failed at GCNCParser(d) step:",err
                try:
                    y = x.parse()
                except Exception, err:
                    print "failed at x.parse step:",err
                try:
                    serializer = Tagged()
                    serializer.write(y,fo)
                except Exception, err:
                    print f2
                    print "Couldnt serialize it:",err
            except Exception, err:
                print "Problem parsing %s" % f2
                print "Error: %s" % err


if __name__ == '__main__':
    main()
