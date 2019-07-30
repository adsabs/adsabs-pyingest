#!/usr/bin/env python

from argparse import ArgumentParser
import urllib
import urllib2
import json
import sys

class URLError(Exception):
    pass

class RequestError(Exception):
    pass

class DataError(Exception):
    pass

class HSTParser():

# HSTParser will return a list of articles taken from a HST API
# (https://proper.stsci.edu/proper/adsProposalSearch/query)

    def __init__(self):
        self.errors = []
        pass

    def get_buffer(self, url, **kwargs):
        if url.find('adsProposalSearch') == -1:
            raise URLError("This parser is only for the HST adsProposalSearch search.")
        if not kwargs.has_key('api_key'):
            raise RequestError('No API key provided to query the HST API.')
        token = kwargs['api_key']
        del kwargs['api_key']
        buff = {}
        qparams = urllib.urlencode(kwargs)
        try:
            req = urllib2.Request("%s?%s"%(url, qparams))
            req.add_header('Content-type', 'application/json')
            req.add_header('Accept', 'text/plain')
            req.add_header('apiKey', token)
            resp = urllib2.urlopen(req)
            buff = json.load(resp)
        except Exception, err:
            raise URLError("Request to HST blew up: %s"%err)
        return buff

    def is_complete(self, rec):
        required_fields = ['bibstem','title','authorNames','date','link','comment','journalCode','affiliations','authorOrcidIdentifiers']
        return all(elem in rec.keys()  for elem in required_fields)

    def add_orcids(self, affs, orcids):
        if len(affs) != len(orcids):
            raise DataError('Affiliation and ORCID arrays have different lengths!')
        afflist = []
        for i in range(len(affs)):
            if orcids[i]:
                afflist.append('%s <ID system="ORCID">%s</ID>' % (affs[i], orcids[i].replace('http://orcid.org/','')))
            else:
                afflist.append(affs[i])
        return afflist

    def parse(self, url, **kwargs):

        hst_props = [{}]
        # retrieve data from HST API
        data = self.get_buffer(url, **kwargs)
        # process the new records
        for d in data['programs']:
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
                    sys.stderr.write('Found misaligned affiliation/ORCID arrays: %s\n'%d['bibstem'])
                    self.errors.append('Found misaligned affiliation/ORCID arrays: %s'%d['bibstem'])
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
                sys.stderr.write('Found record with missing data: %s\n'%recid)
                self.errors.append('Found record with missing data: %s'%recid)
                continue
        return hst_props
