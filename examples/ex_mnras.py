'''
MNRAS parsing example
'''
from pyingest.parsers.oup import OUPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter
import argparse

outfile = 'mnras.tag'

test_files = ['/proj/ads/abstracts/data/MNRAS/504.1/TagTextFiles/stab770.xml',
              '/proj/ads/abstracts/data/MNRAS/504.4/TagTextFiles/stab367.xml',
              ]

def main():

    parser = OUPJATSParser()

    documents = []

    do_refs = False

    for f in test_files:
        try:
            with open(f,'r') as fp:
                input_data = fp.read()
                doc = parser.parse(input_data)
                documents.append(doc)
        except Exception as err:
            print("Error in MNRAS (OUP) parser:", f, err)

    # Write everything out in Classic tagged format
    serializer = Tagged()
    with open(outfile,'w') as ftag:
        for d in documents:
            try:
                serializer.write(d,ftag)
            except Exception as err:
                print("Error in serialization:", err)

# ref_handler = ReferenceWriter()

    # ref_handler.writeref(d,'oup')

if __name__ == '__main__':
    main()
