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

class JATSParser(BaseXmlToDictParser):

    def __init__(self):
    # make sure we are utf-8 clean on stdout, stderr
        self.JATS_SCHEMA = ""

    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
# this returns the root of a JATS article, which is the element <article>
        r = d.get('article',{})
        return r

    def _attribs(self, r, **kwargs):
        kl = self._dict(r).keys()
        attribs = {}
        for k in kl:
            if k[0] == '@':
                attribs[k] = r[k]
        return attribs


    def parse(self, fp, **kwargs):

        output_metadata=dict()

        r = self.resource_dict(fp, **kwargs)

        article_attr = self._attribs(r)
        front_meta = r.get('front')
        back_meta = r.get('back')

        try:
            front_keys, back_keys = (front_meta.keys(),back_meta.keys())
        except AttributeError:
            return
        else:
            article_meta = front_meta.get('article-meta')
            journal_meta = front_meta.get('journal-meta')
            try:
                article_keys, journal_keys = (article_meta.keys(),back_meta.keys())
            except AttributeError:
                return
            else:

# Title
                try:
                    output_metadata['title'] = article_meta['title-group']['article-title']
                except KeyError:
                    pass

# Abstract
                try:
                    output_metadata['abstract'] = article_meta['abstract']['p']
                except KeyError:
                    pass

# Keywords
                try:
                    art_cats = article_meta['article-categories']
                except KeyError:
                    pass
                else:
                    for c in art_cats['subj-group']:
                        if c['@subj-group-type'] == 'toc-minor':
                            output_metadata['keywords'] = c['subject'].replace(',',';')
            
# Pubdate
                try:
                    pub_dates = article_meta['pub-date']
                except KeyError:
                    pass
                else:
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
                    if output_metadata['pubdate'][-2:] == '00':
                         output_metadata['pubdate'] = output_metadata['pubdate'][0:-2]+'01'

# Author Affil(s)
# Data passed to output_metadata with Authors

                affils = {}

                try:
                    notes_meta = article_meta['author-notes']
                    affils[notes_meta['fn']['@id']] = "<EMAIL>" + notes_meta['fn']['p']['email'] + "</EMAIL>"
                except KeyError:
                    pass

                try:
                    affil_meta = article_meta['contrib-group']['aff']
                    for a in affil_meta:
                        affils[a['@id']] = a['institution'] + ', ' + a['#text']
                except KeyError:
                    pass

# Author(s)
                authors = list(dict())
                try:
                    author_meta = article_meta['contrib-group']['contrib']
                    for a in author_meta:
                        if self._attr(a,'contrib-type') == 'author':
                            author_name = a['name']['surname']+", "+a['name']['given-names']
                            author_xref = a['xref']
                            if type(author_xref) == type([]):
                                xref_id = ''
                                for x in author_xref:
                                    xref_id = xref_id + " " + x['@rid']
                            else:
                                xref_id = author_xref['@rid']
                            author_afftag = xref_id.split()
                            authors.append({'name': author_name, 'affil': author_afftag})
                    if len(authors) > 0:
                        for x in authors:
                            auth_list = [x['name'] for x in authors]
                            aff_list = [x['affil'] for x in authors]
                            output_metadata['authors'] = '; '.join(auth_list)
                            output_metadata['affiliations'] = list()
                        for x in aff_list:
                            aff_string=''
                            for y in x:
                                aff_string = aff_string + '; ' + affils[y]
                            output_metadata['affiliations'].append(aff_string)
                        
                except KeyError:
                    pass

# DOI
                try:
                    id_meta = article_meta['article-id']
                    if id_meta['@pub-id-type'] == 'doi':
                        output_metadata['properties'] = {'DOI': 'doi:'+id_meta['#text']}
                except KeyError:
                    pass

# Journal
                try:
                    j_info = journal_meta['journal-title-group']
                except KeyError:
                    pass
                else:
                    output_metadata['journal'] = j_info['journal-title']
# Journal-pub-id
                try:
                    for i in journal_meta['journal-id']:
                        if i['@journal-id-type'] == 'publisher-id':
                            output_metadata['pub-id'] = i['#text']
                except KeyError:
                    pass

# Volume
                try:
                    output_metadata['volume'] = article_meta['volume']
                except KeyError:
                    pass

# Pages
                try:
                    output_metadata['page'] = article_meta['fpage'] + "-" + article_meta['lpage']
                except KeyError:
                    pass

# Issue
                try:
                    output_metadata['issue'] = article_meta['issue']
                except KeyError:
                    pass
       



        return output_metadata





if __name__ == "__main__":
 
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
 
    jatsx = JATSParser()
 
    woo = None
    with open('/Users/mtempleton/adsaps.work/fulltext.xml','rU') as fp:
        woo = jatsx.parse(fp)
 
    print(woo)
