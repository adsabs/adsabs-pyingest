#!/usr/bin/env python

import sys
import json
import codecs
#from adsputils import u2asc
from default import BaseXmlToDictParser

class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass

class UnparseableException(Exception):
    pass


class APSJATSParser(BaseXmlToDictParser):

    def __init__(self):
    # make sure we are utf-8 clean on stdout, stderr
        self.JATS_SCHEMA = ""


    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
        r = d.get('article',{})
        return r

    def check_schema(self, r):
        schema_spec = []
        for s in self._array(r[u'@xmlns:oai_dc']):
            schema_spec.append(self._text(s))
        if len(schema_spec) == 0:
            raise NoSchemaException("Unknown record schema.")
        elif schema_spec[0] != self.DUBC_SCHEMA:
            raise WrongSchemaException("Wrong schema.")
        else:
            pass

    def get_tag(self, r, tag):
        value = []
        for s in self._array(r.get(tag,[])):
            value.append(self._text(s))
        if len(value) == 0:
            value = None
        return value


    def parse(self, fp, **kwargs):

        output_metadata=dict()

        r = self.resource_dict(fp, **kwargs)
        back_matter = r.get('back',{})
        body_matter = r.get('body',{})
        metadata = r.get('front').get('article-meta')

        idtag = None

        if metadata:
# Abstract
            output_metadata['abstract'] = metadata['abstract']['p']
# Title
            output_metadata['title'] = metadata['title-group']['article-title']
# Keywords
            art_cats = metadata['article-categories']
            for c in art_cats['subj-group']:
                if c['@subj-group-type'] == 'toc-minor':
                    output_metadata['keywords'] = c['subject'].replace(',',';')

# Pubdate
            pub_dates = metadata['pub-date']
            for d in pub_dates:
                if d['@publication-format'] == 'print':
                    fulldate = d['@iso-8601-date'].split('-')
                    output_metadata['pubdate'] = fulldate[1]+"/"+fulldate[0]

# Authors & Affils
            affil=dict()

            note_data = metadata['author-notes']
            id_string = note_data['fn']['@id']
            affil[id_string] = note_data['fn']['p']['email']
            auth_data = metadata['contrib-group']
            for a in auth_data['aff']:
                id_string = a['@id']
                affil[id_string] = a['institution'] + ', ' + a['#text']
            auth_list = []
            for a in auth_data['contrib']:
                if a['@contrib-type'] == 'author':
                    name = a['name']['surname']+', '+a['name']['given-names']
                    affs = a['xref']
                    if type(affs) != type(list()):
                        auth_list.append((name,affs['@rid']))
                    else:
                        foo = []
                        for x in affs:
                            foo.append(x['@rid'])
                        auth_list.append((name,'; '.join(foo)))
            alnew = []
            aanew = []
            for (n,a) in auth_list:
                a_aff=a.replace(';','').split()
                auth_affil = ''
                for x in a_aff:
                    auth_affil = auth_affil + affil[x] + "; "
                auth_affil = auth_affil.rstrip('; ')
                aanew.append(auth_affil)
                alnew.append(n)
            output_metadata['authors']=alnew
            output_metadata['affiliations']=aanew



# Bibcode
#       if idtag is not None:
#           output_metadata['bibcode'] = self.make_dubc_bibcode(idtag)



        return output_metadata
## 
# 
#if __name__ == "__main__":
# 
#     sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
#     sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
# 
#     jatsx = APSJATSParser()
# 
#     woo = None
#     with open('/Users/mtempleton/adsaps.work/fulltext.xml','rU') as fp:
#         woo = jatsx.parse(fp)
# 
#     print(woo)
