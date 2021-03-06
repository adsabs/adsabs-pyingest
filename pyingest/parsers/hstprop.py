#!/usr/bin/env python

from past.utils import old_div
import sys
import math
import requests


class URLError(Exception):
    pass


class RequestError(Exception):
    pass


class DataError(Exception):
    pass


class HSTParser(object):
    # HSTParser will return a list of articles taken from a HST API
    # (https://proper.stsci.edu/proper/adsProposalSearch/query)

    def __init__(self):
        self.errors = []
        pass

    def get_batch(self, api_token, api_url, **kwargs):
        get_header = {'apiKey': api_token, 'Accept': 'text/plain',
                      'Content-type': 'application/json'}
        buff = requests.get(api_url, headers=get_header, params=kwargs).json()
        return buff

    def get_records(self, url, **kwargs):
        if url.find('adsProposalSearch') == -1:
            raise URLError("This parser is only for the HST adsProposalSearch search.")
#       if not kwargs.has_key('api_key'):
        if 'api_key' not in kwargs:
            raise RequestError('No API key provided to query the HST API.')
        token = kwargs['api_key']
        del kwargs['api_key']
        buff = {}
        # Store the value of maxRecords, if this was set
        maxrecs = kwargs.get('maxRecords', 200)
        # First get 1 record to determine the total amount of records
        kwargs['maxRecords'] = 1
        # Do the first query
        try:
            batch = self.get_batch(token, url, **kwargs)
        except Exception as err:
            raise URLError("Request to HST blew up: %s" % err)
        # How many records are there?
        totrecs = batch['query']['total']
        # Store the first batch of records
        records = batch['programs']
        # How often do we need to paginate to get them all?
        num_paginates = int(math.ceil(old_div(totrecs, (1.0 * maxrecs))))
        # If we run in test mode, do not paginate
        if kwargs.get('test'):
            num_paginates = 0
        # We harvested the first record to get the total number of records,
        # so we continue with the 2nd
        offset = 1
        kwargs['maxRecords'] = maxrecs
        for i in range(num_paginates):
            kwargs['offset'] = offset
            try:
                batch = self.get_batch(token, url, **kwargs)
            except Exception as err:
                raise URLError("Request to HST blew up: %s" % err)
            records += batch['programs']
            offset += maxrecs
        return records

    def is_complete(self, rec):
        required_fields = ['bibstem', 'title', 'authorNames', 'date', 'link', 'comment', 'journalCode', 'affiliations', 'authorOrcidIdentifiers']
        return all(elem in list(rec.keys()) for elem in required_fields)

    def add_orcids(self, affs, orcids):
        if len(affs) != len(orcids):
            raise DataError('Affiliation and ORCID arrays have different lengths!')
        afflist = []
        for i in range(len(affs)):
            if orcids[i]:
                afflist.append('%s <ID system="ORCID">%s</ID>' % (affs[i], orcids[i].replace('http://orcid.org/', '')))
            else:
                afflist.append(affs[i])
        return afflist

    def parse(self, url, **kwargs):

        hst_props = [{}]
        # retrieve data from HST API
        data = self.get_records(url, **kwargs)
        # process the new records
        for d in data:
            if self.is_complete(d):
                # The "journal field" is a composite from the "journalCode" and "comment" fields:
                #  1. journalCode: expression of mission cycle ('HST Proposal. Cycle NN' or 'JWST Proposal. Cycle N')
                #  2. comment: preformatted as 'HST Proposal#xxxx' or 'JWST Proposal#xxxx'
                # What will go into the 'publication' field will have the form: HST Proposal. Cycle 26, ID. #15676
                journal = "%s, ID. #%s" % (d['journalCode'], d['comment'].split('#')[-1])
                # The ORCID information will have to be inserted into the affiliation information
                try:
                    affils = self.add_orcids(d['affiliations'], d['authorOrcidIdentifiers'])
                except DataError:
                    sys.stderr.write('Found misaligned affiliation/ORCID arrays: %s\n' % d['bibstem'])
                    self.errors.append('Found misaligned affiliation/ORCID arrays: %s' % d['bibstem'])
                    affils = d['affiliations']

                hst_props.append({'bibcode': d['bibstem'],
                                  'authors': d['authorNames'],
                                  'affiliations': affils,
                                  'title': d['title'],
                                  'pubdate': d['date'],
                                  'publication': journal,
                                  'abstract': d['abstract'],
                                  'properties': {'data': d['link']}})
            else:
                recid = d.get('comment') or d.get('bibstem')
                sys.stderr.write('Found record with missing data: %s\n' % recid)
                self.errors.append('Found record with missing data: %s' % recid)
                continue
        return hst_props
