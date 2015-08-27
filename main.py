import sys
import os.path
#sys.path.append(os.path.dirname(__file__))

import codecs
from parsers.zenodo import ZenodoParser
from validators.ads import SimpleValidator
from serializers.classic import Tagged

if __name__ == "__main__":

    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    parser = ZenodoParser()
    validator = SimpleValidator()
    serializer = Tagged()
    for file in sys.argv[1:]:
        d = None
        with open(file, 'r') as fp:
            d = parser.parse(fp)
            validator.validate(d)
            serializer.write(d)

