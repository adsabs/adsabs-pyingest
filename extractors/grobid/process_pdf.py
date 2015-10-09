#!/usr/bin/python
#


import os
import requests
import codecs
import logging
import argparse
import multiprocessing
import time

GROBID_SERVER = 'http://localhost:8081'
GROBID_HANDLER = 'processFulltextDocument'
DEFAULT_THREADS = multiprocessing.cpu_count() / 2;
DEFAULT_TIMEOUT = 60       # timeout on connection after this delay
DEFAULT_MAX_RETRIES = 3    # try to reconnect these many times to grobid server
DEFAULT_SLEEP_DELAY = 10   # give server enough time to restart grobid

class GrobidError(Exception):
    pass

class ConnectionError(Exception):
    pass


class GrobidProcessor(object):
    """
    Needed to take avantage of multiprocessing.Pool
    """
    def __init__(self, service, destdir=None, force=None, timeout=DEFAULT_TIMEOUT,
                 max_retries=DEFAULT_MAX_RETRIES, sleep_delay=DEFAULT_SLEEP_DELAY):
        self.service = service
        self.destdir = destdir
        self.force = force
        self.timeout = timeout
        self.max_retries = max_retries
        self.sleep_delay = sleep_delay

    def __call__(self, file):
        try: 
            fp = open(file, 'r')
        except IOError, error:
            logging.error("error opening file %s: %s" % (file, error))
            return None
        if self.destdir:
            out_file = os.path.join(self.destdir, os.path.basename(file)) + '.xml'
        else:
            out_file = file + '.xml'

        logging.debug("considering source file %s" % file)
        if os.path.exists(out_file):
            if os.path.getmtime(out_file) > os.path.getmtime(file):
                if self.force: 
                    logging.debug("forcing reprocessing of source file %s (target is %s)" %(file, out_file))
                else:
                    logging.debug("target file %s is up-to-date" % out_file)
                    return out_file
            else:
                logging.debug("recreating stale target file %s" % out_file)
        else:
            logging.debug("creating target file %s" % out_file)
            
        logging.info("processing file %s" % file)
        retry = self.max_retries
        while retry > 0:
            try:
                xml = self.send_to_grobid(fp)
            except ConnectionError, error:
                retry = retry - 1
                logging.info("ran into connection error: '%s'" % error)
                if retry > 0:
                    logging.info("retrying in %d seconds" % self.sleep_delay)
                    time.sleep(self.sleep_delay)
            except GrobidError, error:
                logging.error("error processing file %s: %s" % (file, error))
                return None
            else:
                retry = 0

        try:
            fp = codecs.open(out_file, 'w', 'utf-8')
        except IOError, error:
            logging.error("error opening file %s: %s" % (out_file, error))
            return None
        fp.write(xml)
        logging.info("written output file %s" % out_file)
        return out_file


    def send_to_grobid(self, filehandle):
        try:
            response = requests.post(url=self.service, files={'input': filehandle}, timeout=self.timeout)
        except requests.exceptions.Timeout:
            logging.debug("timeout from requests")
            raise ConnectionError("request timeout after %d seconds" % self.timeout)
        except requests.exceptions.RequestException as e:
            raise ConnectionError("request exception: %s" % e)
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
        '--force',
        default=False,
        action='store_true',
        dest='force',
        help='force recreation of all target files'
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
    argp.add_argument(
        '--destdir',
        type=str,
        default=None,
        dest='destdir',
        help='specify output directory for extracted files'
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

    # avoid the overhead of multiprocessing unless necessary
    if threads > 1:
        p = multiprocessing.Pool(threads)
        p.map(GrobidProcessor(service, destdir=args.destdir, force=args.force), args.files)
    else:
        map(GrobidProcessor(service, destdir=args.destdir, force=args.force), args.files)



    
            
