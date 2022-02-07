#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import string
from .jats import JATSParser
from .author_init import AuthorInitial
from pyingest.config.config import *
from pyingest.parsers.entity_convert import EntityConverter


class NoSchemaException(Exception):
    pass


class WrongSchemaException(Exception):
    pass


class UnparseableException(Exception):
    pass


class AIPJATSParser(JATSParser):

    AST_WORDS = [x.lower() for x in UAT_ASTRO_KEYWORDS]
    AST_WORDS = AST_WORDS + [x.lower() for x in AAS_ASTRO_KEYWORDS]
    AST_WORDS = AST_WORDS + [x.lower() for x in APS_ASTRO_KEYWORDS]

    def aip_journals(self, pid):
        try:
            bibstem = AIP_PUBLISHER_IDS[pid]
        except KeyError as err:
            return 'XSTEM'
        else:
            return bibstem

    def parse(self, input_data, **kwargs):

        output_metadata = super(self.__class__, self).parse(input_data, **kwargs)

        document = self.resource_dict(input_data, **kwargs)

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
                    output_metadata['issue']
                except TypeError:
                    pass
                else:
                    pubstring = pubstring + ', Issue ' + output_metadata['issue']

                try:
                    output_metadata['page']
                except Exception as err:
                    pass
                else:
                    if "-" in output_metadata['page']:
                        pubstring = pubstring + ', pp.' + output_metadata['page']
                    else:
                        pubstring = pubstring + ', id.' + output_metadata['page']
                        if 'numpages' in output_metadata:
                            pubstring = pubstring + ', ' + output_metadata['numpages'] + ' pp.'
                            del(output_metadata['numpages'])
            output_metadata['publication'] = pubstring

        try:
            if 'pub-id' in output_metadata:
                bibstem_id = output_metadata['pub-id']
            elif 'coden' in output_metadata:
                bibstem_id = output_metadata['coden']
            j_bibstem = self.aip_journals(bibstem_id)
        except KeyError as err:
            pass
        else:
            year = output_metadata['pubdate'][-4:]
            bibstem = j_bibstem.ljust(5, '.')
            volume = output_metadata['volume'].rjust(4, '.')
            if j_bibstem == 'AIPC':
                issue_letter = string.ascii_letters[int(output_metadata['page'][0:2]) - 1]
            else:
                issue_letter = string.ascii_letters[int(output_metadata['issue'])-1]
            if "-" in output_metadata['page']:
                idno = output_metadata['page']
            else:
                idno = output_metadata['page'].split('-')
            if len(idno) == 6:
                try:
                    idtwo = string.ascii_letters[int(idno[0:2]) - 1]
                except Exception as err:
                    idtwo = idno[0:2]
                idfour = idno[2:]
            else:
                idtwo = ''
                idfour = idno.rjust(4, '.')
            idno = idfour
            try:
                a = AuthorInitial()
                author_init = a.get_author_init(output_metadata['authors'])
            except Exception as err:
                print(err)
                author_init = '.'
            output_metadata['bibcode'] = year + bibstem + volume + issue_letter + idno + author_init

    
        # Return
        return output_metadata
