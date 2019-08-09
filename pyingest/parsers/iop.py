#!/usr/bin/env python

import sys
import json
import codecs
import string
from adsputils import u2asc
from jats import JATSParser
from pyingest.config.config import *

class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass

class UnparseableException(Exception):
    pass


class IOPJATSParser(JATSParser):

    AST_WORDS = [x.lower() for x in UAT_ASTRO_KEYWORDS]

    def get_author_init(self,namestring):
        output = u2asc(namestring)
        for c in output:
            if c.isalpha():
                return c.upper()
        return u'.'

    def iop_journals(self, pid):
#       mapping journal-meta/journal-id/publisher-id to bibstems
#       IOP_PUBLISHER_IDS = {}
#       IOP_PUBLISHER_IDS['rnaas'] = u'RNAAS'
        try:
            bibstem = IOP_PUBLISHER_IDS[pid]
        except KeyError:
            return 'XSTEM'
        else:
            return bibstem

    def dbfromkw(self, d, **kwargs):
        db = []
        if isinstance(d,basestring):
            keywords = d.split(',')
            for k in keywords:
                if k.lower() in self.AST_WORDS:
                    db.append('AST')
                    return db
        return db


    def parse(self, fp, **kwargs):

        output_metadata = super(self.__class__, self).parse(fp, **kwargs)



# Publication +
        try:
            pubstring = output_metadata['publication']
        except:
            pass
        else:
            try:
                output_metadata['volume']
            except:
                pass
            else:
                pubstring = pubstring +', Volume '+ output_metadata['volume']
            
            try:
                pubstring = pubstring +', Issue '+ output_metadata['issue']
            except TypeError:
                pass
            
            try:
                output_metadata['page']
            except:
                pass
            else:
                pubstring = pubstring +', id.'+ output_metadata['page']

            output_metadata['publication'] = pubstring
            
# Bibcode
        try:
            j_bibstem = self.iop_journals(output_metadata['pub-id'])
        except KeyError:
            pass
        else:
            year = output_metadata['pubdate'][-4:]
            bibstem = j_bibstem.ljust(5,'.')
            volume = output_metadata['volume'].rjust(4,'.')
            if output_metadata['pub-id'] == 'rnaas':
                issue_letter = string.letters[int(output_metadata['issue'])-1]
            else:
                issue_letter = '.'
            idno = output_metadata['page']
            if len(idno) == 6:
                idtwo = string.letters[int(idno[0:2])]
                idfour = idno[2:]
            else:
                idtwo = ''
                idfour = idno.rjust(4,'.')
            idno = idtwo + idfour
            try:
            #   author_init = self.get_author_init(output_metadata['authors'][0])
                author_init = self.get_author_init(output_metadata['authors'])
            except:
                author_init = '.'
            output_metadata['bibcode'] = year + bibstem + volume + issue_letter + idno + author_init
            del output_metadata['pub-id']
            del output_metadata['page']

# Database (from APS keywords)
        try:
            output_metadata['database'] = self.dbfromkw(output_metadata['keywords'])
        except:
            pass
            


# Return
        return output_metadata
