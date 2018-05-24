#!/usr/bin/env python

import cgi
import json
import re
import sys
from adsputils import u2asc
from default import BaseBeautifulSoupParser


class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass

class UnparseableException(Exception):
    pass

class JATSParser(BaseBeautifulSoupParser):

    def __init__(self):
        pass

    def resource_dict(self, fp, **kwargs):
        d = self.bstodict(fp, **kwargs)
# this returns the root of a JATS article, which is the element <article>
        r = d.article
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

    def _munge(self, r):
# to retain any formatting tags inside a beautifulsoup tag, you need to 
# turn it into a string with prettify(), and then split the string 
# on linefeeds and remove multiple blank spaces.
        if type(r) is not type(None):
            s = (' '.join(r.prettify().split('\n'))).lstrip().rstrip()
            t = re.sub('\s{2,}',' ',s)
            try:
                x1 = re.search('<.*?> ',t).group()
                x2 = re.sub('<','</',x1)
                x3 = re.sub(' .*?>','>',x2.rstrip())
                u = t.replace(x1,'').replace(x3,'')
                v = u.replace(x3,'')
            except:
                v = t
            return v.lstrip().rstrip()
        else:
            return ''


    def parse(self, fp, **kwargs):

        output_metadata=dict()

        r = self.resource_dict(fp, **kwargs)

        article_meta = r.front.find('article-meta')
        journal_meta = r.front.find('journal-meta')

        base_metadata = {}

#Title:
        title = article_meta.find('title-group').find('article-title')
        base_metadata['title'] = self._munge(title)
        base_metadata['title'] = self._dehtml(base_metadata['title'])


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
                key = n['id']
                note_text_arr = [x.get_text() for x in n]
                note_text = ' '.join(note_text_arr)
                affils[key] = note_text

#     # Affils/affil ids
        try:
            affil = article_meta.find('contrib-group').find_all('aff')
        except:
            pass
        else:
            for a in affil:
                key = a['id']
                num = key.lstrip('a') 
                aff_text = a.get_text().lstrip(num)
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
                    surname = a.surname.get_text()
                else:
                    surname = 'Anonymous'
                if a.find('prefix') is not None:
                    prefix = a.prefix.get_text()+' '
                else:
                    prefix = ''
                if a.find('suffix') is not None:
                    suffix = ' '+a.suffix.get_text()
                else:
                    suffix = ''
                if a.find('given-names') is not None:
                    given = a.find('given-names').get_text()
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


#Abstract:
        try:
            abstract = article_meta.abstract.p
        except:
            pass
        else:
            base_metadata['abstract'] = self._munge(abstract)
            base_metadata['abstract'] = self._dehtml(base_metadata['abstract'])

#Keywords:
        keywords = article_meta.find('article-categories').find_all('subj-group')
        for c in keywords:
            if c['subj-group-type'] == 'toc-minor':
                base_metadata['keywords'] = self._munge(c.subject)

#Volume:
        volume = article_meta.volume
        base_metadata['volume'] = self._munge(volume)

#Issue:
        issue = article_meta.issue
        base_metadata['issue'] = self._munge(issue)

#Journal name:
        journal = journal_meta.find('journal-title-group').find('journal-title')
        base_metadata['publication'] = self._munge(journal)

#Journal ID:
        jid = journal_meta.find_all('journal-id')
        for j in jid:
            if j['journal-id-type'] == 'publisher-id':
                base_metadata['pub-id'] = self._munge(j)

#DOI:
        ids = article_meta.find_all('article-id')
        for d in ids:
            if d['pub-id-type'] == 'doi':
                base_metadata['properties'] = {'DOI': 'doi:'+self._munge(d)}

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
                del fpage
        try:
            fpage
        except NameError:
            pass
        else:
            lpage = article_meta.lpage
            if lpage == None:
                del lpage
            else:
                if lpage == fpage:
                    del lpage
            try:
                lpage
            except NameError:
                base_metadata['page'] = self._munge(fpage)
            else:
                base_metadata['page'] = self._munge(fpage) + "-" + self._munge(lpage)


        output_metadata = base_metadata
        return output_metadata
















