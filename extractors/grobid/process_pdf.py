#!/usr/bin/python
#


import os
import requests
import codecs
import logging
import argparse
import multiprocessing

GROBID_SERVER = 'http://localhost:8081'
GROBID_HANDLER = 'processFulltextDocument'
DEFAULT_THREADS = multiprocessing.cpu_count() / 2;

class GrobidError(Exception):
    pass


class GrobidProcessor(object):
    """
    Needed to take avantage of multiprocessing.Pool
    """
    def __init__(self, service):
        self.service = service

    def __call__(self, file):
        try: 
            fp = open(file, 'r')
        except IOError, error:
            logging.error("error opening file %s: %s" % (file, error))
            return False
        logging.info("processing file %s" % file)
        try:
            xml = self.send_to_grobid(fp)
        except GrobidError, error:
            logging.error("error processing file %s: %s" % (file, error))
            return False
        out_file = file + '.xml'
        try:
            fp = codecs.open(out_file, 'w', 'utf-8')
        except IOError, error:
            logging.error("error opening file %s: %s" % (out_file, error))
            return False
        fp.write(xml)
        logging.info("written output file %s" % out_file)
        return True

    def send_to_grobid(self, filehandle):
        response = requests.post(url=self.service, files={'input': filehandle})
        if response.status_code == 200:
            logging.debug("successful response from grobid server (%d bytes)" % len(response.content))
            return response.text
        else:
            raise GrobidError("HTTP %d - %s: %s" % (response.status_code, response.reason, response.text))


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
    argp.add_argument(
        '--threads',
        type=int,
        default=DEFAULT_THREADS,
        dest='threads',
        help='specify number of threads to use (default is %d)' % DEFAULT_THREADS
        )
    argp.add_argument('files', nargs='+')
    return argp.parse_args()


if __name__ == "__main__":
    
    args = parse_arguments()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    service = os.path.join(args.server, args.handler)

    threads = min(args.threads, len(args.files))
    logging.info("allocating %d threads for processing %d files" %(threads, len(args.files)))

    p = multiprocessing.Pool(threads)
    p.map(GrobidProcessor(service), args.files)


    
            
