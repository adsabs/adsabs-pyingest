#!/usr/bin/env python

import sys
import os
import json
import codecs
import string
from adsputils import u2asc
from jats import JATSParser
from pyingest.config.config import *
from pyingest.parsers.entity_convert import EntityConverter
from author_names import AuthorNames

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


    def get_author_init(self,namestring):
        output = u2asc(namestring)
        for c in output:
            if c.isalpha():
                return c.upper()
        return u'.'

    def aip_journals(self, pid):
        try:
            bibstem = AIP_PUBLISHER_IDS[pid]
        except KeyError, err:
            return 'XSTEM'
        else:
            return bibstem

    def parse(self, fp, **kwargs):

        output_metadata = super(self.__class__, self).parse(fp, **kwargs)

        fp.seek(0)
        document = self.resource_dict(fp, **kwargs)

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
                pubstring = pubstring +', Volume '+ output_metadata['volume']
            
                try:
                    output_metadata['issue']
                except TypeError:
                    pass
                else:
                    pubstring = pubstring +', Issue '+ output_metadata['issue']

                try:
                    output_metadata['page']
                except Exception, err:
                    pass
                else:
                    if "-" in output_metadata['page']:
                        pubstring = pubstring + ', pp.' + output_metadata['page']
                    else:
                        pubstring = pubstring + ', id.' + output_metadata['page']
            output_metadata['publication'] = pubstring
        # Bibcode
        try:
            if 'pub-id' in output_metadata.keys():
                bibstem_id = output_metadata['pub-id']
            elif 'coden' in output_metadata.keys():
                bibstem_id = output_metadata['coden']
            j_bibstem = self.aip_journals(bibstem_id)
        except KeyError, err:
            pass
        else:
            year = output_metadata['pubdate'][-4:]
            bibstem = j_bibstem.ljust(5,'.')
            volume = output_metadata['volume'].rjust(4,'.')
            if j_bibstem == 'AIPC':
                issue_letter = string.letters[int(output_metadata['page'][0:2]) - 1]
            else:
                issue_letter = string.letters[int(output_metadata['issue'])-1]
            idno = output_metadata['page']
            if len(idno) == 6:
                try:
                    idtwo = string.letters[int(idno[0:2]) - 1]
                except Exception, err:
                    idtwo = idno[0:2]
                idfour = idno[2:]
            else:
                idtwo = ''
                idfour = idno.rjust(4,'.')
            idno = idfour
            try:
                author_init = self.get_author_init(output_metadata['authors'])
            except Exception, err:
                author_init = '.'
            output_metadata['bibcode'] = year + bibstem + volume + issue_letter + idno + author_init

        # pass relevant fields through EntityConverter
        # to remove bad entities
        # entity_fields = ['abstract', 'title', 'authors', 'affiliations']
        entity_fields = ['abstract', 'title', 'authors']
        # entity_fields = ['abstract', 'title']
        for ecf in entity_fields:
            if ecf in output_metadata.keys():
                try:
                    conv = EntityConverter()
                    conv.input_text = output_metadata[ecf]
                    conv.convert()
                    output_metadata[ecf] = conv.output_text
                except Exception, err:
                    print "problem converting %s for %s: %s" % (ecf, output_metadata['bibcode'], err)
    
        # Return
        return output_metadata

