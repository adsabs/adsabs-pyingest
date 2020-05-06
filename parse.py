""" Example parser """
import sys
import os.path

import logging
import logging.config
import codecs
import json

from pyingest.config.logging import loggingDict
from pyingest.config.utils import import_class, parse_arguments

sys.path.append(os.path.dirname(__file__))


if __name__ == "__main__":

    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    ARGS = parse_arguments()
    if ARGS.debug:
        loggingDict['loggers']['']['level'] = 'DEBUG'
    logging.config.dictConfig(loggingDict)

    # it is probably more user-friendly do do this kind
    # of configuration via a config file (see ConfigParser)
    logging.debug("parser set to %s" % ARGS.parser)
    PARSER = import_class(ARGS.parser)
    logging.debug("validator set to %s" % ARGS.validator)
    VALIDATOR = import_class(ARGS.validator)
    logging.debug("serializer set to %s" % ARGS.serializer)
    SERIALIZER = import_class(ARGS.serializer)

    for file in ARGS.files:
        d = None
        with open(file) as fp:
            logging.debug("parsing file %s" % file)
            try:
                # If a Zenodo records happens to be missing a DOI,
                # we don't want an Exception to have the process crap out
                # In that case skip the file and write a message to stderr
                d = PARSER.parse(fp)
            except Exception as err:
                sys.stderr.write("unable to parse file: %s (%s)\n"
                                 % (file, err))
                logging.debug("unable to parse file: %s (%s)" % (file, err))
                continue
            if ARGS.debug:
                sys.stderr.write("document: %s" % json.dumps(d))
            logging.debug("validating file %s" % file)
            VALIDATOR.validate(d)
            logging.debug("serializing file %s" % file)
            SERIALIZER.write(d)
