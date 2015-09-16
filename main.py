import sys
import os.path
#sys.path.append(os.path.dirname(__file__))

import logging
import logging.config
import argparse
import codecs
from parsers.zenodo import ZenodoParser
from validators.ads import SimpleValidator
from serializers.classic import Tagged
from config.logging import loggingDict

if __name__ == "__main__":

    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    argp = argparse.ArgumentParser()
    argp.add_argument(
        '--debug',
        default=False,
        action='store_true',
        dest='debug',
        help='turn on debugging'
        )
    argp.add_argument('files', nargs='+')
    args = argp.parse_args()
    if args.debug:
        loggingDict['loggers']['']['level'] = 'DEBUG';
    logging.config.dictConfig(loggingDict)
        
    parser = ZenodoParser()
    validator = SimpleValidator()
    serializer = Tagged()
    for file in args.files:
        d = None
        with open(file, 'r') as fp:
            logging.debug("parsing file %s" %file)
            d = parser.parse(fp)
            logging.debug("validating file %s" %file)
            validator.validate(d)
            logging.debug("serializing file %s" %file)
            serializer.write(d)

