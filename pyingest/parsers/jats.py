#!/usr/bin/env python

import sys
import json
import codecs
from adsputils import u2asc
from default import BaseXmlToDictParser
from xmltodict import unparse

class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass

class UnparseableException(Exception):
    pass

class JATSParser(BaseXmlToDictParser):

    def __init__(self):
        pass

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

    def _gettext(self, r):
        if isinstance(r,list):
            return "; ".join(self._gettext(x) for x in r)
        elif isinstance(r,tuple):
            return ": ".join(self._gettext(x) for x in r)
        elif isinstance(r,dict):
            return self._gettext(r.items())
        elif isinstance(r,basestring):
            return r



    def parse(self, fp, **kwargs):

        output_metadata=dict()

# The storage of the raw jats data is a kludge to deal with cases where you
# need to deal with titles and/or abstracts with <inline-formula>s.  See
# the Title and Abstract sections below.

        raw_jats_data = fp.read()

        r = self.resource_dict(raw_jats_data, **kwargs)


#       article_attr = self._attribs(r)
        front_meta = r.get('front')
#       back_meta = r.get('back')

        try:
#           front_keys, back_keys = (front_meta.keys(),back_meta.keys())
            front_keys = front_meta.keys()
        except AttributeError:
            raise WrongSchemaException("Could not parse front and back matter.")
        else:
            article_meta = front_meta.get('article-meta')
            journal_meta = front_meta.get('journal-meta')
            try:
                article_keys, journal_keys = (article_meta.keys(),journal_meta.keys())
            except AttributeError:
                raise WrongSchemaException("Could not parse article and journal metadata.")
            else:
                base_metadata = {}

#Title:
                try:
                    title = article_meta['title-group']['article-title']
                except:
                    pass
                else:
                    if isinstance(title,unicode):
                        base_metadata['title'] = title
                    else:
                        base_metadata['title'] = raw_jats_data.split('<title-group>')[1].split('<article-title>')[1].split('</article-title>')[0].decode('utf-8')

#Abstract:
                try:
                    abstract = article_meta['abstract']['p']
                except:
                    pass
                else:
                    if isinstance(abstract,unicode):
                        base_metadata['abstract'] = abstract
                    else:
                        try:
                            base_metadata['abstract'] = raw_jats_data.split('<abstract>')[1].split('<p>')[1].split('</p>')[0].decode('utf-8')
                        except:
                            pass

#Authors and Affiliations: 
#Affiliations first:
                affils = {}
#Affil notes first:
                try:
                    notes_meta = article_meta['author-notes']
                except KeyError:
                    pass
                else:
                    try:
                        note = self._array(notes_meta['fn'])
                    except KeyError:
                        pass
                    else:
                        for n in note:
                            try:
                                affils[self._attr(n,'id')] = self._gettext(n['p']) 
                            except:
                                try:
                                    affils[self._attr(n,'id')] = self._gettext(n)
                                except:
                                    affils[self._attr(n,'id')] = ''
                        
                try:
                    contrib_group = self._array(article_meta['contrib-group'])
                except:
                    pass
                else:
                    for g in contrib_group:
                        try:
                            affil_meta = self._array(g['aff'])
                        except KeyError:
                            pass
                        else:
                            for a in affil_meta:
                                try:
                                    a['institution']
                                except KeyError:
                                    a['institution']=''
                                try:
                                    if type(a['institution']) == type(list()):
                                        li = [x for x in a['institution'] if isinstance(x,basestring)]
                                        a['institution'] = li
                                        affils[self._attr(a,'id')] = ', '.join(a['institution']) + ', ' + self._text(a)
                                    else:
                                        affils[self._attr(a,'id')] = a['institution'] + ', ' + self._text(a)
                                except KeyError:
                                    pass
                 
                        

#Authors and note keys
                    for g in contrib_group:
                        try:
                            author_meta = self._array(g['contrib'])
                        except KeyError:
                            pass
                        else:
                            base_metadata['authors'] = list()
                            base_metadata['affiliations'] = list()
                            for a in author_meta:
                                if self._attr(a,'contrib-type') == 'author':
                                    try:
                                        pre = a['name']['prefix']+' '
                                    except:
                                        pre = ''
                                    if pre == None:
                                        pre = ''
                                    try:
                                        suf = ' '+a['name']['suffix']
                                    except:
                                        suf = ''
                                    if suf == None:
                                        suf = ''
                                    try:
                                        sur = a['name']['surname']
                                    except:
                                        sur = 'Anonymous'
                                    try:
                                        giv = a['name']['given-names'].rstrip()
                                    except:
                                        giv = ''
                                    if giv == None:
                                        pre = ''
                                    if (pre+giv+suf) == '':
                                        base_metadata['authors'].append(sur)
                                    else:
                                        base_metadata['authors'].append(sur+", "+pre+giv+suf)
                                    try:
                                        affs = self._array(a['xref'])
                                        aid = self._gettext([self._attr(x,'rid') for x in affs]).replace(';',' ').split()
                                    except:
                                        base_metadata['affiliations'].append('')
                                    else:
                                        aff_string = "; ".join([affils[x] for x in aid])
                                        base_metadata['affiliations'].append(aff_string)
                            base_metadata['authors'] = "; ".join(base_metadata['authors'])

#Keywords:
                try:
                    art_cats = article_meta['article-categories']['subj-group']
                except:
                    pass
                else:
                    if type(art_cats) == type(list()):
                        for c in art_cats:
                            if c['@subj-group-type'] == 'toc-minor':
                                base_metadata['keywords'] = c['subject'].replace(',',';')            
                    else:
                        if art_cats['@subj-group-type'] == 'toc-minor':
                            base_metadata['keywords'] = art_cats['subject'].replace(',',';')            


#Pubdate:
                try:
                    pub_dates = article_meta['pub-date']
                except:
                    pass
                else:
                    if(type(pub_dates)) == type(list()):
                        for d in pub_dates:
                            a = self._attr(d,'publication-format')
                            b = self._attr(d,'pub-type')
                            if (a == 'print' or b == 'ppub'):
                                base_metadata['pubdate'] = self._attr(d,'iso-8601-date')
                                if base_metadata['pubdate'][-2:] == '00':
                                    base_metadata['pubdate'] = base_metadata['pubdate'][0:-2]+'01'
                            else:
                                if (b == 'epub'):
                                    base_metadata['pubdate'] = self._attr(d,'iso-8601-date')
                                    if base_metadata['pubdate'][-2:] == '00':
                                        base_metadata['pubdate'] = base_metadata['pubdate'][0:-2]+'01'
                    else:
                        a = self._attr(pub_dates,'publication-format')
                        b = self._attr(pub_dates,'pub-type')
                        if (a == 'print' or b == 'ppub'):
                            base_metadata['pubdate'] = self._attr(pub_dates,'iso-8601-date')
                            if base_metadata['pubdate'][-2:] == '00':
                                base_metadata['pubdate'] = base_metadata['pubdate'][0:-2]+'01'
                        else:
                            if (b == 'epub'):
                                base_metadata['pubdate'] = self._attr(pub_dates,'iso-8601-date')
                                if base_metadata['pubdate'][-2:] == '00':
                                    base_metadata['pubdate'] = base_metadata['pubdate'][0:-2]+'01'

#DOI:
                try:
                    id_meta = article_meta['article-id']
                    try:
                        if self._attr(id_meta,'pub-id-type') == 'doi':
                            base_metadata['properties'] = {'DOI': 'doi:'+self._text(id_meta)}
                    except:
                        pass
                except:
                    pass

#Journal name:
                try:
                    base_metadata['publication'] = journal_meta['journal-title-group']['journal-title']
                    if type(base_metadata['publication']) == type(list()):
                        base_metadata['publication'] = base_metadata['publication'][0]
                except:
                    pass
#Journal ID:
                try:
                    for i in journal_meta['journal-id']:
                        if self._attr(i,'journal-id-type') == 'publisher-id':
                            base_metadata['pub-id'] = self._text(i)
                except:
                    pass

#Volume:
                try:
                    base_metadata['volume'] = article_meta['volume']
                except:
                    pass

#Issue:
                try:
                    base_metadata['issue'] = article_meta['issue']
                except:
                    pass

#Pages:
                try:
                    fpage = article_meta['fpage']
                except:
                    try:
                        fpage = article_meta['elocation-id']
                    except:
                        pass
                try:
                    fpage
                except NameError:
                    pass
                else:
                    try:
                        lpage = article_meta['lpage']
                    except KeyError:
                        pass
                    else:
                        if lpage == fpage:
                            del lpage
                    try:
                        lpage
                    except NameError:
                        base_metadata['page'] = fpage
                    else:
                        base_metadata['page'] = fpage + "-" + lpage



                output_metadata = base_metadata

        return output_metadata
