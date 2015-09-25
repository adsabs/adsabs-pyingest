#!/usr/bin/python
#


import os
import requests
import logging
import argparse

GROBID_SERVER = 'http://localhost:8081'
GROBID_HANDLER = 'processFulltextDocument'

class GrobidError(Exception):
    pass


def process_one(file, service):
    response = requests.post(url=service, files={'input': file})
    if response.status_code == 200:
        return response.text
    else:
        raise GrobidError(response.reason)

def parse_arguments():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '--debug',
        default=False,
        action='store_true',
        dest='debug',
        help='turn on debugging'
        )
    argp.add_argument(
        '--server',
        type=str,
        default=GROBID_SERVER,
        dest='server',
        help='specify server to use (default is %s)' % GROBID_SERVER
        )
    argp.add_argument(
        '--handler',
        type=str,
        default=GROBID_HANDLER,
        dest='handler',
        help='specify handler to use (default is %s)' % GROBID_HANDLER
        )
    argp.add_argument('files', nargs='+')
    return argp.parse_args()


if __name__ == "__main__":
    
    args = parse_arguments()
    logger = logging.getLogger('Grobid PDF extraction')
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    service = os.path.join(args.server, args.handler)

    for file in args.files:
        logging.info("processing file %s" % file)
        try:
            xml = process_one(file, service)
        except GrobidError, error:
            logging.error("error processing file %s: %s" % (file, error))
            continue
        out_file = file + '.xml'
        with open(file, 'w') as fp:
            fp.write(xml)
        logging.info("written output file %s" % out_file)


    
            
