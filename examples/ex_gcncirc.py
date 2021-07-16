from __future__ import print_function
from glob import glob
from pyingest.parsers.gcncirc import GCNCParser
from pyingest.serializers.classic import Tagged
from namedentities import hex_entities

basedir = './pyingest/tests/data/stubdata/input/gcncirc/'
inputFileList = glob(basedir + '*.gcn3')
outputTagFile = './output.tag'

def main():

    with open(outputTagFile, 'w') as fo:

        for f in inputFileList:
            print(f)
            try:
                with open(f, 'r') as fg:
                    d = fg.read()
            except Exception as err:
                print(f)
                print("couldnt read it:", err)
            else:
                try:
                    x = GCNCParser(d)
                    y = x.parse()
                    serializer = Tagged()
                    serializer.write(y, fo)
                except Exception as err:
                    print(f)
                    print("Couldnt parse it:", err)

if __name__ == '__main__':
    main()
