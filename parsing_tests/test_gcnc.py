from pyingest.parsers.gcncirc import GCNCParser
from pyingest.serializers.classic import Tagged

def main():

    flist = ['23456.gcn3','23457.gcn3','23458.gcn3','25321.gcn3','9999.gcn3']
    basedir = '/Users/mtempleton/Projects/GCN_Parser/gcn3/'

    with open('output.tag','w') as fo:
        for f in flist:
            f2 = basedir + f
            with open(f2,'rU') as fg:
                d = fg.read()
            x = GCNCParser(d)
            y = x.parse()
            # print "\n\n"
            # print 'lol y:',y
            serializer = Tagged()
            serializer.write(y,fo)


if __name__ == '__main__':
    main()
