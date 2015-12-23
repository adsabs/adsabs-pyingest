import sys
import os.path

import logging
import logging.config
import codecs
import json

sys.path.append(os.path.dirname(__file__))
from config.logging import loggingDict
from config.utils import import_class, parse_arguments


if __name__ == "__main__":

    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    args = parse_arguments()
    if args.debug:
        loggingDict['loggers']['']['level'] = 'DEBUG';
    logging.config.dictConfig(loggingDict)

    # it is probably more user-friendly do do this kind
    # of configuration via a config file (see ConfigParser)
    logging.debug("parser set to {}".format(args.parser))
    parser = import_class(args.parser)
    logging.debug("validator set to {}".format(args.validator))
    validator = import_class(args.validator)
    logging.debug("serializer set to {}".format(args.serializer))
    serializer = import_class(args.serializer)

    for file in args.files:
        d = None
        with open(file) as fp:
            logging.debug("parsing file %s" %file)
            d = parser.parse(fp)
            if args.debug:
                sys.stderr.write("document: %s" % json.dumps(d))
            logging.debug("validating file %s" %file)
            validator.validate(d)
            logging.debug("serializing file %s" %file)
            serializer.write(d)

