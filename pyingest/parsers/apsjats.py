#!/usr/bin/env python

import sys
import json
import codecs
from adsputils import u2asc
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

    def get_author_init(self,namestring):
        output = u2asc(namestring)
        for c in output:
            if c.isalpha():
                return c
        return u'.'

    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
        r = d.get('article',{})
        return r

    def aps_journals(self, pid):
#       mapping journal-meta/journal-id/publisher-id to bibstems
        publisher_ids = {'PRL': 'PhRvL', 'PRX': 'PhRvX', 'RMP': 'RvMP',
                         'PRA': 'PhRvA', 'PRB': 'PhRvB', 'PRC': 'PhRvC',
                         'PRD': 'PhRvD', 'PRE': 'PhRvE', 'PRAB': 'PhRvS',
                         'PRSTAB': 'PhRvS', 'PRAPPLIED': 'PhRvP',
                         'PRFLUIDS': 'PhRvF', 'PRMATERIALS': 'PhRvM', 
                         'PRPER': 'PRPER', 'PRSTPER': 'PRSTP', 'PR': 'PhRv',
                         'PRI': 'PhRvI'}
        try:
            bibstem = publisher_ids[pid]
        except KeyError:
            return 'XSTEM'
        else:
            return bibstem

    def doi_parse(self, doi):
        doi_string = doi[4:].split('/')[1]
        doi_array = doi_string.split('.')
        vol , idsix = doi_array[1], doi_array[2]
        vol = vol.rjust(4,'.')
        idtwo = chr(96+int(idsix[0:2]))
        idfour = idsix[2:]
        return vol, idtwo + idfour
        

    def parse(self, fp, **kwargs):

        output_metadata=dict()

        r = self.resource_dict(fp, **kwargs)
        back_matter = r.get('back',{})
        body_matter = r.get('body',{})
        metadata = r.get('front').get('article-meta')
        journaldata = r.get('front').get('journal-meta')


        try:
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
                try:
                   d['@publication-format']
                except KeyError:
                   try:
                       d['@pub-type']
                   except KeyError:
                       pass
                   else:
                       if d['@pub-type'] == 'ppub':
                           output_metadata['pubdate'] = d['@iso-8601-date']
                else:
                   if d['@publication-format'] == 'print':
                       output_metadata['pubdate'] = d['@iso-8601-date']

# Authors & Affils
            affil=dict()
            note_data = metadata['author-notes']
            id_string = note_data['fn']['@id']
#           affil[id_string] = note_data['fn']['p']['email']
            affil[id_string] = note_data['fn']['p']
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
            output_metadata['authors']='; '.join(alnew)
            output_metadata['affiliations']=aanew

# DOI
            id_info = metadata['article-id']
            if id_info['@pub-id-type'] == 'doi':
                output_metadata['properties'] = {'DOI': 'doi:'+id_info['#text']}

# Journal
            j_info = journaldata['journal-title-group']
            j_name = j_info['journal-title']
            j_short = j_info['abbrev-journal-title']
            for i in journaldata['journal-id']:
                if i['@journal-id-type'] == 'publisher-id':
                    j_bibstem = self.aps_journals(i['#text'])

# Bibcode
            year = output_metadata['pubdate'][0:4]
            bibstem = j_bibstem.ljust(5,'.')
            volume, idno = self.doi_parse(output_metadata['properties']['DOI'])
            author_init = self.get_author_init(output_metadata['authors'])
            output_metadata['bibcode'] = year + bibstem + volume + idno + author_init
        except:
# send to logger?
            print "parsing failed."
        else:
            pass

        return output_metadata
## 
# 
#if __name__ == "__main__":
# 
#    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
#    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
# 
#    jatsx = APSJATSParser()
# 
#    woo = None
#    with open('/Users/mtempleton/adsaps.work/fulltext.xml','rU') as fp:
#        woo = jatsx.parse(fp)
# 
#    print(woo)
