#!/usr/bin/env python

import bs4
from collections import OrderedDict
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
        newr = bs4.BeautifulSoup(unicode(r), 'lxml')
        tag_list = list(set([x.name for x in newr.find_all()]))
        for t in tag_list:
            if t in JATS_TAGS_DANGER:
                newr.find(t).decompose()
            elif t in tags_keep:
                newr.find(t).contents
            else:
                newr.find(t).unwrap()
        return unicode(newr).replace("  ", " ")

    def resource_dict(self, fp, **kwargs):
        d = self.bsfiletodict(fp, **kwargs)
        r = self.bsstrtodict(unicode(d.article), **kwargs)
        return r

    def parse(self, fp, **kwargs):

        output_metadata = dict()

        document = self.resource_dict(fp, **kwargs)
        r = document.front

        article_meta = r.find('article-meta')
        journal_meta = r.find('journal-meta')

        back_meta = document.back

        base_metadata = {}

# Title:
        title = article_meta.find('title-group').find('article-title')
        try:
            title.xref.extract()
        except Exception as e:
            pass
        try:
            title.fn.extract()
        except Exception as e:
            pass
        base_metadata['title'] = (
            self._detag(title, JATS_TAGSET['title']).strip())

# Abstract:
        try:
            abstract = article_meta.abstract.p
        except Exception as e:
            pass
        else:
            base_metadata['abstract'] = (
                self._detag(abstract, JATS_TAGSET['abstract']))


# Authors and Affiliations:
        # Set up affils storage
        affils = OrderedDict()

        # Author notes/note ids
        try:
            notes = article_meta.find('author-notes').find_all('fn')
        except Exception as e:
            pass
        else:
            for n in notes:
                n.label.decompose()
                key = n['id']
                note_text = self._detag(n, JATS_TAGSET['affiliations'])
                affils[key] = note_text.strip()

        # Affils/affil ids
        try:
            affil = article_meta.find('contrib-group').find_all('aff')
        except Exception as e:
            pass
        else:
            for a in affil:
                try:
                    a.label.decompose()
                except Exception as e:
                    pass
                key = a['id']
                ekey = ''
                try:
                    email_a = a.find('ext-link')
                    a.find('ext-link').extract()
                    if email_a['ext-link-type'] == 'email':
                        address = self._detag(email_a, (
                            JATS_TAGSET['affiliations']))
                        address_new = "<EMAIL>" + address + "</EMAIL>"
                        ekey = email_a['id']
                except Exception as e:
                    pass

                aff_text = self._detag(a, JATS_TAGSET['affiliations'])
                affils[key] = aff_text.strip()
                if ekey is not '':
                    affils[ekey] = address_new


# Author name and affil/note lists:
        try:
            authors = article_meta.find('contrib-group').find_all('contrib')
        except Exception as e:
            pass
        else:
            base_metadata['authors'] = []
            base_metadata['affiliations'] = []
            for a in authors:

                # ORCIDs
                orcid_out = None
                try:
                    orcids = a.find_all('ext-link')
                    for o in orcids:
                        try:
                            if o['ext-link-type'] == 'orcid':
                                orcid_out = (
                                    "<ID system=\"ORCID\">"+self._detag(o, (
                                     [])+"</ID>"))
                        except Exception as e:
                            pass
                except Exception as e:
                    pass

                # Author names
                if a.find('surname') is not None:
                    surname = self._detag(a.surname, [])
                else:
                    surname = 'Anonymous'
                if a.find('prefix') is not None:
                    prefix = self._detag(a.prefix, [])+' '
                else:
                    prefix = ''
                if a.find('suffix') is not None:
                    suffix = ' '+self._detag(a.suffix, [])
                else:
                    suffix = ''
                if a.find('given-names') is not None:
                    given = self._detag(a.find('given-names'), [])
                else:
                    given = ''
                forename = prefix+given+suffix
                if forename == '':
                    base_metadata['authors'].append(surname)
                else:
                    base_metadata['authors'].append(surname + ', ' + forename)

                # Author affil/note ids
                aid = a.find_all('xref')
                if len(aid) > 0:
                    aid_str = ' '.join([x['rid'] for x in aid])
                    aid_arr = aid_str.split()
                else:
                    aid_arr = []

                try:
                    new_aid_arr = []
                    for a in affils.keys():
                        if a in aid_arr:
                            new_aid_arr.append(a)
                    aid_arr = new_aid_arr

                    aff_text = '; '.join(affils[x] for x in aid_arr)
                    aff_text = aff_text.replace(';;', ';').rstrip(';')

                    # Got ORCID?
                    if orcid_out is not None:
                        aff_text = aff_text + '; ' + orcid_out
                    base_metadata['affiliations'].append(aff_text)
                except Exception as error:
                    if orcid_out is not None:
                        base_metadata['affiliations'].append(orcid_out)
                    else:
                        base_metadata['affiliations'].append('')

            if len(base_metadata['authors']) > 0:
                base_metadata['authors'] = "; ".join(base_metadata['authors'])
            else:
                del base_metadata['authors']

# Copyright:
        try:
            copyright = article_meta.find('copyright-statement')
        except Exception as e:
            pass
        else:
            base_metadata['copyright'] = self._detag(copyright, [])

# Keywords:
        keywords = article_meta.find('article-categories').find_all('subj-group')
        for c in keywords:
            if c['subj-group-type'] == 'toc-minor':
                base_metadata['keywords'] = self._detag(c.subject, (
                    JATS_TAGSET['keywords']))
        if 'keywords' not in base_metadata:
            try:
                keywords = article_meta.find('kwd-group').find_all('kwd')
                kwd_arr = []
                for c in keywords:
                    kwd_arr.append(self._detag(c, JATS_TAGSET['keywords']))
                if len(kwd_arr) > 0:
                    base_metadata['keywords'] = ', '.join(kwd_arr)
            except Exception as e:
                pass

# Volume:
        volume = article_meta.volume
        base_metadata['volume'] = self._detag(volume, [])

# Issue:
        issue = article_meta.issue
        base_metadata['issue'] = self._detag(issue, [])

# Journal name:
        journal = journal_meta.find('journal-title-group').find('journal-title')
        base_metadata['publication'] = self._detag(journal, [])

# Journal ID:
        jid = journal_meta.find_all('journal-id')
        for j in jid:
            if j['journal-id-type'] == 'publisher-id':
                base_metadata['pub-id'] = self._detag(j, [])

# DOI:
        ids = article_meta.find_all('article-id')
        for d in ids:
            if d['pub-id-type'] == 'doi':
                base_metadata['properties'] = {'DOI': self._detag(d, [])}

# Pubdate:

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
            try:
                pubdate = "/" + self._detag(d.year, [])
                try:
                    d.month
                except Exception as e:
                    pubdate = "00" + pubdate
                else:
                    try:
                        int(self._detag(d.month, []))
                    except Exception as err:
                        month_name = self._detag(d.month, [])[0:3].lower()
                        month = MONTH_TO_NUMBER[month_name]
                    else:
                        month = self._detag(d.month, [])
                    if month < 10:
                        month = "0"+str(month)
                    else:
                        month = str(month)
                    pubdate = month + pubdate
            except Exception as err:
                print "Error in pubdate:", err
            else:
                if (a == 'print' or b == 'ppub'):
                    base_metadata['pubdate'] = pubdate
                elif (a == 'electronic' or b == 'epub'):
                    try:
                        base_metadata['pubdate']
                    except Exception as e:
                        base_metadata['pubdate'] = pubdate

# Pages:

        fpage = article_meta.fpage
        if fpage is None:
            fpage = article_meta.find('elocation-id')
            if fpage is None:
                fpage = article_meta.pageStart
                if fpage is None:
                    del fpage
        try:
            fpage
        except NameError:
            pass
        else:
            lpage = article_meta.lpage
            if lpage is None:
                lpage = article_meta.pageEnd
                if lpage is None:
                    del lpage
            else:
                if lpage == fpage:
                    del lpage
            try:
                lpage
            except NameError:
                base_metadata['page'] = self._detag(fpage, [])
            else:
                base_metadata['page'] = self._detag(fpage, []) + "-" + (
                    self._detag(lpage, []))


# References (now using back_meta):
#       try:
#           reflist = back_meta.find('ref-list').find_all('ref')
#       except Exception as e:
#           print "References:", e
#       else:
#           for ref in reflist:
#               print ref.find('ext-link')

        output_metadata = base_metadata
        return output_metadata
