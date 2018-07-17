#!/usr/bin/env python

import bs4
from default import BaseBeautifulSoupParser
from pyingest.config.config import *


class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass

class UnparseableException(Exception):
    pass

class JATSParser(BaseBeautifulSoupParser):

    def __init__(self):
        pass

    def _detag(self, r, tags_keep, **kwargs):
        newr = bs4.BeautifulSoup(unicode(r),"lxml")
        tag_list = list(set([x.name for x in newr.find_all()]))
        for t in tag_list:
            if t in JATS_TAGS_DANGER:
                newr.find(t).decompose()
            elif t in tags_keep:
                newr.find(t).contents
            else:
                newr.find(t).unwrap()
        return unicode(newr).replace("  "," ")

    def resource_dict(self, fp, **kwargs):
        d = self.bsfiletodict(fp, **kwargs)
        r = self.bsstrtodict(unicode(d.article), **kwargs)
        return r


    def parse(self, fp, **kwargs):

        output_metadata=dict()

        r = self.resource_dict(fp, **kwargs).front

        article_meta = r.find('article-meta')
        journal_meta = r.find('journal-meta')

        base_metadata = {}

#Title:
        title = article_meta.find('title-group').find('article-title')
        base_metadata['title'] = self._detag(title,JATS_TAGSET['title'])

#Abstract:
        try:
            abstract = article_meta.abstract.p
        except:
            pass
        else:
            base_metadata['abstract'] = self._detag(abstract,JATS_TAGSET['abstract'])


#Authors and Affiliations:
#     # Set up affils storage
        affils = {}

#     # Author notes/note ids 
        try:
            notes = article_meta.find('author-notes').find_all('fn')
        except:
            pass
        else:
            for n in notes:
                n.label.decompose()
                key = n['id']
                note_text = self._detag(n,JATS_TAGSET['affiliations'])
                affils[key] = note_text

#     # Affils/affil ids
        try:
            affil = article_meta.find('contrib-group').find_all('aff')
        except:
            pass
        else:
            for a in affil:
                try:
                    a.label.decompose()
                except:
                    pass
                key = a['id']
                aff_text = self._detag(a,JATS_TAGSET['affiliations'])
                affils[key] = aff_text
        

#Author name and affil/note lists:
        try:
            authors = article_meta.find('contrib-group').find_all('contrib')
        except:
            pass
        else:
            base_metadata['authors']=[]
            base_metadata['affiliations']=[]
            for a in authors:
#             # Author names
                if a.find('surname') is not None:
                    surname = self._detag(a.surname,[])
                else:
                    surname = 'Anonymous'
                if a.find('prefix') is not None:
                    prefix = self._detag(a.prefix,[])+' '
                else:
                    prefix = ''
                if a.find('suffix') is not None:
                    suffix = ' '+self._detag(a.suffix,[])
                else:
                    suffix = ''
                if a.find('given-names') is not None:
                    given = self._detag(a.find('given-names'),[])
                else:
                    given = ''
                forename = prefix+given+suffix
                if forename == '':
                    base_metadata['authors'].append(surname)
                else:
                    base_metadata['authors'].append(surname+', '+forename)

#             # Author affil/note ids
                aid = a.find_all('xref')
                if len(aid) > 0:
                    aid_str = ' '.join([x['rid'] for x in aid])
                    aid_arr = aid_str.split()
                else:
                    aid_arr = []

                aff_text = '; '.join(affils[x] for x in aid_arr) 
                base_metadata['affiliations'].append(aff_text)
             
            


            if len(base_metadata['authors']) > 0:
                base_metadata['authors'] = "; ".join(base_metadata['authors'])
            else:
                del base_metadata['authors']


#Keywords:
        keywords = article_meta.find('article-categories').find_all('subj-group')
        for c in keywords:
            if c['subj-group-type'] == 'toc-minor':
                base_metadata['keywords'] = self._detag(c.subject,JATS_TAGSET['keywords'])

#Volume:
        volume = article_meta.volume
        base_metadata['volume'] = self._detag(volume,[])

#Issue:
        issue = article_meta.issue
        base_metadata['issue'] = self._detag(issue,[])

#Journal name:
        journal = journal_meta.find('journal-title-group').find('journal-title')
        base_metadata['publication'] = self._detag(journal,[])

#Journal ID:
        jid = journal_meta.find_all('journal-id')
        for j in jid:
            if j['journal-id-type'] == 'publisher-id':
                base_metadata['pub-id'] = self._detag(j,[])

#DOI:
        ids = article_meta.find_all('article-id')
        for d in ids:
            if d['pub-id-type'] == 'doi':
                base_metadata['properties'] = {'DOI': 'doi:'+self._detag(d,[])}

#Pubdate:

        pub_dates = article_meta.find_all('pub-date')
        for d in pub_dates:
            try:
                a = d['publication-format']
            except KeyError:
                a = ''
            try:
                b = d['pub-type']
            except KeyError:
                b = ''
            if (a == 'print' or b == 'ppub'):
                base_metadata['pubdate'] = d['iso-8601-date']
                if base_metadata['pubdate'][-2:] == '00':
                    base_metadata['pubdate'] = base_metadata['pubdate'][0:-2]+'01'
            else:
                if (a == 'electronic' or b == 'epub'):
                    try:
                         base_metadata['pubdate']
                    except KeyError:
                        base_metadata['pubdate'] = d['iso-8601-date']
                        if base_metadata['pubdate'][-2:] == '00':
                            base_metadata['pubdate'] = base_metadata['pubdate'][0:-2]+'01'
                    else:
                        pass
#Pages:

        fpage = article_meta.fpage
        if fpage == None:
            fpage = article_meta.find('elocation-id')
            if fpage == None:
                fpage = article_meta.pageStart
                if fpage == None:
                    del fpage
        try:
            fpage
        except NameError:
            pass
        else:
            lpage = article_meta.lpage
            if lpage == None:
                lpage = article_meta.pageEnd
                if lpage == None:
                    del lpage
            else:
                if lpage == fpage:
                    del lpage
            try:
                lpage
            except NameError:
                base_metadata['page'] = self._detag(fpage,[])
            else:
                base_metadata['page'] = self._detag(fpage,[]) + "-" + self._detag(lpage,[])

        output_metadata = base_metadata
        return output_metadata

