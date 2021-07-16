from __future__ import print_function
from glob import glob
from pyingest.parsers.gcncirc import GCNCParser
from pyingest.serializers.classic import Tagged

basedir = './pyingest/tests/data/stubdata/input/gcncirc/'
inputFileList = glob(basedir + '*.gcn3')
outputTagFile = './output.tag'

def main():

    documents = list()
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
                documents.append(x.parse())
            except Exception as err:
                print(f)
                print("Couldnt parse it:", err)
    if documents:
        with open(outputTagFile, 'w') as fo:
            serializer = Tagged()
            for doc in documents:
                try:
                    serializer.write(doc, fo)
                except Exception as err:
                    print(err)
               

if __name__ == '__main__':
    main()
