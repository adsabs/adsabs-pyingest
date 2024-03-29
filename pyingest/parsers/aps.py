#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
from past.builtins import basestring
from .jats import JATSParser
from .author_init import AuthorInitial
from pyingest.config.config import *


class NoSchemaException(Exception):
    pass


class WrongSchemaException(Exception):
    pass


class UnparseableException(Exception):
    pass


class APSJATSParser(JATSParser):

    AST_WORDS = [x.lower() for x in APS_ASTRO_KEYWORDS]

    def aps_journals(self, pid):
        # mapping journal-meta/journal-id/publisher-id to bibstems
        try:
            bibstem = APS_PUBLISHER_IDS[pid]
        except KeyError as err:
            print("Warning, APS bibstem not found!")
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

    def parse(self, input_data, **kwargs):

        output_metadata = super(self.__class__, self).parse(input_data, **kwargs)

        # Publication +
        try:
            pubstring = output_metadata['publication']
        except Exception as err:
            pass
        else:
            try:
                output_metadata['volume']
            except Exception as err:
                pass
            else:
                pubstring = pubstring + ', Volume ' + output_metadata['volume']

            try:
                pubstring = pubstring + ', Issue ' + output_metadata['issue']
            except TypeError:
                pass

            try:
                output_metadata['page']
            except Exception as err:
                pass
            else:
                pubstring = pubstring + ', id.' + output_metadata['page']
                if 'numpages' in output_metadata:
                    pubstring = pubstring + ', ' + output_metadata['numpages'] + ' pp.'
                    del(output_metadata['numpages'])

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
                a = AuthorInitial()
                author_init = a.get_author_init(output_metadata['authors'])
            except Exception as err:
                print(err)
                author_init = '.'
            output_metadata['bibcode'] = year + bibstem + volume + idno + author_init
            del output_metadata['pub-id']

        # Database (from APS keywords)
        try:
            output_metadata['database'] = self.dbfromkw(output_metadata['keywords'])
        except Exception as err:
            pass

        # Return
        return output_metadata
