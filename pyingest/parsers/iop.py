#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
from past.builtins import basestring
import string
import logging, sys
from pyingest.config.utils import u2asc
from .jats import JATSParser
from .author_init import AuthorInitial
from pyingest.config.config import *
from pyingest.parsers.entity_convert import EntityConverter

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
# change to logging.INFO or logging.WARNING to turn off

class NoSchemaException(Exception):
    pass


class WrongSchemaException(Exception):
    pass


class UnparseableException(Exception):
    pass


class IOPJATSParser(JATSParser):

    def iop_journals(self, pid):
        # mapping journal-meta/journal-id/publisher-id to bibstems
        # IOP_PUBLISHER_IDS = {}
        # IOP_PUBLISHER_IDS['rnaas'] = u'RNAAS'
        try:
            bibstem = IOP_PUBLISHER_IDS[pid]
        except KeyError:
            return 'XSTEM'
        else:
            return bibstem

    def dbfromkw(self, d, **kwargs):
        db = []
        if isinstance(d, basestring):
            keywords = d.split(',')
            for k in keywords:
                # if k.lower() in AST_WORDS:
                if k in AST_WORDS:
                    db.append('AST')
                    return db
                elif 'UAT:' in k.lower():
                    db.append('AST')
                    return db
        return db
    
    def dbfrombs(self, d, bs):
        db = []
        logging.debug(bs)
        try:
            bibs = IOP_PUBLISHER_IDS[bs]
        except KeyError:
            return 'XSTEM'
        else:
            logging.debug(bibs)
            if bibs == 'ApJ':
                db.append('AST')
            elif bibs == 'apjl':
                db.append('AST')
            elif bibs == 'apjs':
                db.append('AST')
            elif bibs == 'aj':
                db.append('AST')
            elif bibs == 'jcap':
                db.append('AST')
                return db
            elif bibs == 'psj':
                db.append('AST')
            elif bibs == 'raa':
                db.append('AST')
            elif bibs == 'rnaas':
                db.append('AST')
            elif bibs == 'pasp':
                db.append('AST')
            else:
                db.append('PHY')
        return db


    def parse(self, input_data, **kwargs):
        output_metadata = super(self.__class__, self).parse(input_data, parser='lxml', **kwargs)

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
                page_id = output_metadata['page']
            except Exception as err:
                pass
            else:
                if "-" in page_id:
                    pubstring = pubstring + ', pp.' + page_id
                else:
                    pubstring = pubstring + ', id.' + page_id
                    if 'numpages' in output_metadata:
                        pubstring = pubstring + ', ' + output_metadata['numpages'] + ' pp.'
                        del(output_metadata['numpages'])
     
            output_metadata['publication'] = pubstring

        # Bibcode
        try:
            j_bibstem = self.iop_journals(output_metadata['pub-id'])
        except KeyError:
            pass
        else:
            year = output_metadata['pubdate'][-4:]
            logging.debug(year)
            bibstem = j_bibstem.ljust(5, '.')
            logging.debug('bibstem',bibstem)
            logging.debug('j_bibstem',j_bibstem)
            # if bibstem == IOP_PUBLISHER_IDS['jcap']:
            if bibstem == 'JCAP.':
                volume = output_metadata['issue'].rjust(4, '.')
                logging.debug('JCAP bibcode',bibstem)
            else:
                volume = output_metadata['volume'].rjust(4, '.')
            # RNAAS used to have a month-letter in column 14, but it was
            # deprecated September 2019 by CSG
            issue_letter = '.'
            idno = output_metadata['page']
            if "-" in idno:
                idno = idno.split("-")[0]
            else:
                if len(idno) == 6:
                    try:
                        idtwo = string.ascii_letters[int(idno[0:2]) - 1]
                    except Exception as err:
                        print('warning while creating volume/issue for bibcode:',err)
                        idtwo = idno[0:2]
                    idfour = idno[2:]
                    issue_letter = ''
                else:
                    idtwo = ''
                    idfour = idno.rjust(4, '.')
                idno = idtwo + idfour
            try:
                a = AuthorInitial()
                author_init = a.get_author_init(output_metadata['authors'])
            except Exception as err:
                print(err)
                author_init = '.'

            if bibstem == u'ApJL.':
                bibstem = u'ApJ..'
                issue_letter = u'L'
                idno = idno.replace('L', '.')
                
            bib_tail = issue_letter + idno + author_init
            while len(bib_tail) > 6:
                if bib_tail[0] == '.':
                    bib_tail = bib_tail[1:]
                else:
                    bib_tail = bib_tail[1:]

            bib_tail = bib_tail.rjust(6, '.')
            output_metadata['bibcode'] = year + bibstem + volume + bib_tail

            del output_metadata['pub-id']
            del output_metadata['page']

        # Database (from APS keywords)
        try:
            output_metadata['database'] = self.dbfromkw(output_metadata['keywords'])
        except Exception as err:
            pass
        
        # Database (for IOPP parsing)
        try:
            output_metadata['database'] = self.dbfrombs(bibstem)
        except Exception as err:
            pass

        # Return
        return output_metadata
