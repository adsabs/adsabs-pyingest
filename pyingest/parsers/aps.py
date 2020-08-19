#!/usr/bin/env python

import sys
import json
import codecs
from pyingest.config.utils import u2asc
from jats import JATSParser
from pyingest.config.config import *


class NoSchemaException(Exception):
    pass


class WrongSchemaException(Exception):
    pass


class UnparseableException(Exception):
    pass


class APSJATSParser(JATSParser):

    AST_WORDS = [x.lower() for x in APS_ASTRO_KEYWORDS]
    

    def get_author_init(self, namestring):
        output = u2asc(namestring)
        for c in output:
            if c.isalpha():
                return c
        return u'.'

    def aps_journals(self, pid):
        # mapping journal-meta/journal-id/publisher-id to bibstems
        try:
            bibstem = APS_PUBLISHER_IDS[pid]
        except KeyError, err:
            print "Warning, APS bibstem not found!"
            return 'XSTEM'
        else:
            return bibstem

    def dbfromkw(self, d, **kwargs):
        db = ['PHY']
        if isinstance(d, basestring):
            keywords = d.split(',')
            for k in keywords:
                if k.lower() in self.AST_WORDS:
                    db.append('AST')
                    return db
                elif 'UAT:' in k.lower():
                    db.append('AST')
                    return db
        return db

    def parse(self, fp, **kwargs):

        output_metadata = super(self.__class__, self).parse(fp, **kwargs)

        # Publication +
        try:
            pubstring = output_metadata['publication']
        except Exception, err:
            pass
        else:
            try:
                output_metadata['volume']
            except Exception, err:
                pass
            else:
                pubstring = pubstring + ', Volume ' + output_metadata['volume']

            try:
                pubstring = pubstring + ', Issue ' + output_metadata['issue']
            except TypeError:
                pass

            try:
                output_metadata['page']
            except Exception, err:
                pass
            else:
                pubstring = pubstring + ', id.' + output_metadata['page']

            output_metadata['publication'] = pubstring

# Bibcode
        try:
            j_bibstem = self.aps_journals(output_metadata['pub-id'])
        except KeyError:
            pass
        else:
            year = output_metadata['pubdate'][-4:]
            bibstem = j_bibstem.ljust(5, '.')
            volume = output_metadata['volume'].rjust(4, '.')
            idno = output_metadata['page']
            if len(idno) == 6:
                idtwo = chr(96 + int(idno[0:2]))
                idfour = idno[2:]
            else:
                idtwo = ''
                idfour = idno.rjust(5, '.')
            idno = idtwo + idfour
            try:
                author_init = self.get_author_init(output_metadata['authors'][0])
            except Exception, err:
                author_init = '.'
            output_metadata['bibcode'] = year + bibstem + volume + idno + author_init
            del output_metadata['pub-id']

# Database (from APS keywords)
        try:
            output_metadata['database'] = self.dbfromkw(output_metadata['keywords'])
        except Exception, err:
            pass

# Return
        return output_metadata
