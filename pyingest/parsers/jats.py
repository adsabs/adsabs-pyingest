#!/usr/bin/env python

import bs4
# from bs4 import Comment, CData
from bs4 import CData
from collections import OrderedDict
from default import BaseBeautifulSoupParser
from pyingest.config.config import *
from affils import AffiliationParser
from entity_convert import EntityConverter
from uat_key2uri import UATURIConverter
import namedentities
import re
import copy


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

        newr = bs4.BeautifulSoup(unicode(r), 'html5lib')
        try:
            tag_list = list(set([x.name for x in newr.find_all()]))
        except Exception, err:
            tag_list = []
        for t in tag_list:

            if t in JATS_TAGS_DANGER:
                oldr = None
                while oldr != newr:
                    try:
                        oldr = copy.deepcopy(newr)
                        newr.find(t).decompose()
                    except Exception, err:
                        pass
            elif t in tags_keep:
                oldr = None
                while oldr != newr:
                    try:
                        oldr = copy.deepcopy(newr)
                        newr.find(t).contents
                    except Exception, err:
                        pass
            else:
                oldr = None
                while oldr != newr:
                    try:
                        oldr = copy.deepcopy(newr)
                        newr.find(t).unwrap()
                    except Exception, err:
                        pass

        # Note: newr is converted from a bs4 object to unicode here.
        # Everything after this point is string manipulation.

        newr = unicode(newr)

        # amp_pat = r'(?<=&amp\;)(.*?)(?=\;)'
        amp_pat = r'(&amp;)(.*?)(;)'
        amp_fix = re.findall(amp_pat, newr)
        for s in amp_fix:
            s_old = ''.join(s)
            s_new = '&' + s[1] + ';'
            newr = newr.replace(s_old, s_new)

        newr = newr.replace(u'\n', u' ').replace(u'  ', u' ')
        newr = newr.replace('&nbsp;', ' ')

        # CDATA removal
        # cdata_pat = r'(\<.*?CDATA\[*)(.*?)(\]*>)' # csg 2020apr06
        cdata_pat = r'(<inline-formula>.*?CDATA\[*)(.*?)(\]*<\/inline-formula>)' # csg 2020apr30
        cdata = re.findall(cdata_pat, newr)
        for s in cdata:
            s_old = ''.join(s)
            s_new = ' <inline-formula>' + s[1] + '</inline-formula> '
            newr = newr.replace(s_old, s_new)

        return newr

    def resource_dict(self, fp, **kwargs):
        d = self.bsfiletodict(fp, **kwargs)
        r = self.bsstrtodict(unicode(d.article), **kwargs)
        return r

    def parse(self, fp, **kwargs):

        output_metadata = {}

        document = self.resource_dict(fp, **kwargs)
        r = document.front

        try:
            article_meta = r.find('article-meta')
            journal_meta = r.find('journal-meta')
        except Exception, err:
            return {}

        back_meta = document.back

        base_metadata = {}

# Title:
        title_xref_list = []
        title_fn_list = []
        try:
            title = article_meta.find('title-group').find('article-title')
        except Exception, err:
            pass
        else:
            try:
                for dx in title.find_all('xref'):
                    title_xref_list.append(self._detag(dx,
                        JATS_TAGSET['abstract']).strip())
                    dx.decompose()
                # title.xref.decompose()
                # title.xref.extract()
            except Exception, err:
                pass
            try:
                for df in title.find_all('fn'):
                    title_fn_list.append(self._detag(df,
                        JATS_TAGSET['abstract']).strip())
                    df.decompose()
                # title.fn.decompose()
                # title.fn.extract()
            except Exception, err:
                pass
            base_metadata['title'] = (
                self._detag(title, JATS_TAGSET['title']).strip())

# Abstract:
        try:
            abstract = article_meta.abstract.p
        except Exception, err:
            pass
        else:
            try:
                for element in abstract(text=lambda text: isinstance(text, CData)):
                    element.extract()
            except Exception, err:
                pass
            else:
                abstract = (
                    self._detag(abstract, JATS_TAGSET['abstract']))
            base_metadata['abstract'] = abstract
            if title_fn_list:
                base_metadata['abstract'] += '  ' + ' '.join(title_fn_list)


# Authors and Affiliations:
        # Set up affils storage
        affils = OrderedDict()

        # Author notes/note ids
        try:
            notes = article_meta.find('author-notes').find_all('fn')
        except Exception, err:
            pass
        else:
            for n in notes:
                try:
                    n.label.decompose()
                except Exception, err:
                    pass
                else:
                    try:
                        n['id']
                    except Exception, err:
                        pass
                        # print "I'm failing on author notes!",err
                    else:
                        key = n['id']
                        note_text = self._detag(n, JATS_TAGSET['affiliations'])
                        affils[key] = note_text.strip()

        # Affils/affil ids
        l_need_affils = False
        try:
            affil = article_meta.find('contrib-group').find_all('aff')
            if len(affil) == 0:
                try:
                    affil = article_meta.find_all('aff')
                except Exception, err:
                    pass
        except Exception, err:
            pass
        else:
            for a in affil:
                try:
                    a.label.decompose()
                except Exception, err:
                    pass
                try:
                    a['id']
                except Exception, err:
                    # print "I'm failing in the affils loop!",err
                    l_need_affils = True
                else:
                    key = a['id']
                    ekey = ''
                    try:
                        email_array = []
                        email_a = a.find_all('ext-link')
                        for em in email_a:
                            if em['ext-link-type'] == 'email':
                                address = self._detag(em, (
                                    JATS_TAGSET['affiliations']))
                                address_new = "<EMAIL>" + address + "</EMAIL>"
                                ekey = em['id']
                                if ekey is not '':
                                    affils[ekey] = address_new
                        while a.find('ext-link') is not None:
                            a.find('ext-link').extract()
                    except Exception, err:
                        pass

                    aff_text = self._detag(a, JATS_TAGSET['affiliations'])
                    affils[key] = aff_text.strip()
                    # if ekey is not '':
                    #     affils[ekey] = address_new

        # Author name and affil/note lists:
        try:
            authors = article_meta.find('contrib-group').find_all('contrib')
        except Exception, err:
            pass
        else:
            base_metadata['authors'] = []
            base_metadata['affiliations'] = []
            for a in authors:

                # ORCIDs
                orcid_out = None
                try:
                    # orcids = a.find_all('ext-link')
                    orcids = a.find('ext-link')
                    try:
                        if orcids['ext-link-type'] == 'orcid':
                            o = self._detag(orcids, [])
                            orcid_out = "<ID system=\"ORCID\">" + o + "</ID>"
                    except Exception, err:
                        pass
                except Exception, err:
                    pass
                if orcid_out is None:
                    try:
                        if a.find('contrib-id') is not None:
                            auth_id = a.find('contrib-id')
                            if auth_id['contrib-id-type'] == 'orcid':
                                o = self._detag(auth_id, [])
                                o = o.split('/')[-1]
                                orcid_out = "<ID system=\"ORCID\">" + o + "</ID>"
                    except Exception, err:
                        pass

                # If you didn't get affiliations above, l_need_affils == True, so do this...
                if l_need_affils:
                    try:
                        if a.find('aff') is not None:
                            aff_id = a.find('aff')
                            aff_text = self._detag(aff_id, JATS_TAGSET['affiliations'])
                    except Exception, err:
                        pass
                

                # Author names
                if a.find('collab') is not None:
                    base_metadata['authors'].append(self._detag(a.collab, []))
                else:
                    if a.find('surname') is not None:
                        surname = self._detag(a.surname, [])
                    else:
                        surname = ''
                    if a.find('prefix') is not None:
                        prefix = self._detag(a.prefix, []) + ' '
                    else:
                        prefix = ''
                    if a.find('suffix') is not None:
                        suffix = ' ' + self._detag(a.suffix, [])
                    else:
                        suffix = ''
                    if a.find('given-names') is not None:
                        given = self._detag(a.find('given-names'), [])
                    else:
                        given = ''
                    forename = prefix + given + suffix
                    if forename == '':
                        if surname != '':
                            base_metadata['authors'].append(surname)
                        # else:
                            # base_metadata['authors'].append('ANONYMOUS')
                        # check instead whether author array is empty, and
                        # pass an empty array to serializer
                    else:
                        if surname != '':
                            base_metadata['authors'].append(surname + ', ' + forename)
                        else:
                            base_metadata['authors'].append(forename)

                    # EMAIL in contrib-group (e.g. OUP)
                    email = None
                    if a.find('email') is not None:
                        email = self._detag(a.email, [])
                        email = '<EMAIL>' + email + '</EMAIL>'

                # Author affil/note ids
                try:
                    aid = a.find_all('xref')
                except Exception, err:
                    pass
                else:
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

                    # check whether or not you got affil data in one way or the other...
                    if not l_need_affils:
                        aff_text = '; '.join(affils[x] for x in aid_arr)
                    aff_text = aff_text.replace(';;', ';').rstrip(';')
                    aff_text = aff_text.replace('; ,', '').rstrip()

                    # Got ORCID?
                    if orcid_out is not None:
                        aff_text = aff_text + '; ' + orcid_out
                    if email is not None:
                        aff_text = aff_text + ' ' + email
                    base_metadata['affiliations'].append(aff_text)
                except Exception, errrror:
                    if orcid_out is not None:
                        base_metadata['affiliations'].append(orcid_out)
                    else:
                        base_metadata['affiliations'].append('')
                affnew = []
                for affx in base_metadata['affiliations']:
                    affnew.append(AffiliationParser(affx).parse())
                base_metadata['affiliations'] = affnew

            if len(base_metadata['authors']) > 0:
                base_metadata['authors'] = "; ".join(base_metadata['authors'])
            else:
                del base_metadata['authors']

# Copyright:
        try:
            copyright = article_meta.find('copyright-statement')
        except Exception, err:
            pass
        else:
            base_metadata['copyright'] = self._detag(copyright, [])

# Keywords:
        try:
            keys_uat = []
            keys_misc = []
            keys_aas = []
            keyword_groups = article_meta.find_all('kwd-group')
            for kg in keyword_groups:
                # Check for UAT first:
                if kg['kwd-group-type'] == 'author':
                    keys_uat_test = kg.find_all('compound-kwd-part')
                    for kk in keys_uat_test:
                        if kk['content-type'] == 'term':
                            keys_uat.append(self._detag(kk, 
                                JATS_TAGSET['keywords']))
                    if not keys_uat:
                        keys_misc_test = kg.find_all('kwd')
                        for kk in keys_misc_test:
                            keys_misc.append(self._detag(kk, 
                                JATS_TAGSET['keywords']))
                # Then check for AAS:
                elif kg['kwd-group-type'] == 'AAS':
                    keys_aas_test = kg.find_all('kwd')
                    for kk in keys_aas_test:
                        keys_aas.append(self._detag(kk, 
                            JATS_TAGSET['keywords']))
                # If all else fails, just search for 'kwd'
                else:
                    keys_misc_test = kg.find_all('kwd')
                    for kk in keys_misc_test:
                        keys_misc.append(self._detag(kk, 
                            JATS_TAGSET['keywords']))
            if keys_uat:
                keywords = keys_uat
            elif keys_aas:
                keywords = keys_aas
            elif keys_misc:
                keywords = keys_misc
            if keywords:
                base_metadata['keywords'] = ', '.join(keywords)
        except Exception, err:
            pass
        if 'keywords' not in base_metadata:
            try:
                keywords = article_meta.find('article-categories').find_all('subj-group')
            except Exception, err:
                keywords = []
            for c in keywords:
                try:
                    if c['subj-group-type'] == 'toc-minor':
                        klist = []
                        for k in c.find_all('subject'):
                            klist.append(self._detag(k, (
                                JATS_TAGSET['keywords'])))
                        base_metadata['keywords'] = ', '.join(klist)
                except Exception, err:
                    pass

        # Now convert any UAT keywords to their URI:
        try:
            uat_cnv = UATURIConverter()
            base_metadata['keywords'] = uat_cnv.convert_to_uri(base_metadata['keywords'])
        except Exception, err:
            pass


# Volume:
        volume = article_meta.volume
        base_metadata['volume'] = self._detag(volume, [])

# Issue:
        issue = article_meta.issue
        base_metadata['issue'] = self._detag(issue, [])

# Journal name:
        try:
            journal = journal_meta.find('journal-title-group').find('journal-title')
            base_metadata['publication'] = self._detag(journal, [])
        except Exception, err:
            try:
                journal = journal_meta.find('journal-title')
                base_metadata['publication'] = self._detag(journal, [])
            except Exception, err:
                pass

        try:
            jid = journal_meta.find('journal-id', {'journal-id-type':'publisher-id'})
            if jid:
                base_metadata['pub-id'] = self._detag(jid, [])
            else:
                try:
                    jid = journal_meta.find('journal-id', {'journal-id-type':'coden'})
                    if jid:
                        base_metadata['coden'] = self._detag(jid, [])
                except Exception, err:
                    pass
        except Exception, err:
            pass 

# Journal ID:
#        try:
#            jid = journal_meta.find_all('journal-id')
#        except Exception, err:
#            jid = []
#        # use the publisher ID first, otherwise use coden
#        for j in jid:
#            if j['journal-id-type'] == 'publisher-id':
#                base_metadata['pub-id'] = self._detag(j, [])
#        try:
#            base_metadata['pub-id']
#        except Exception, err:
#            for j in jid:
#                if j['journal-id-type'] == 'coden':
#                    base_metadata['pub-id'] = self._detag(j, [])

# links: DOI and arxiv preprints
        # DOI
        base_metadata['properties'] = {}
        try:
            ids = article_meta.find_all('article-id')
        except Exception, err:
            ids = []
        for d in ids:
            if d['pub-id-type'] == 'doi':
                base_metadata['properties']['DOI'] = self._detag(d, [])
        # Arxiv Preprint
        try:
            arxiv = article_meta.find_all('custom-meta')
        except Exception, err:
            pass
        else:
            ax_pref = 'https://arxiv.org/abs/'
            for ax in arxiv:
                try:
                    x_name = self._detag(ax.find('meta-name'),[])
                    x_value = self._detag(ax.find('meta-value'),[])
                    if x_name == 'arxivppt':
                        base_metadata['properties']['HTML'] = ax_pref + x_value
                except Exception, err:
                    pass

# Pubdate:
        try:
            pub_dates = article_meta.find_all('pub-date')
        except Exception, err:
            pub_dates = []
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
                except Exception, err:
                    pubdate = "00" + pubdate
                else:
                    try:
                        int(self._detag(d.month, []))
                    except Exception, errrr:
                        month_name = self._detag(d.month, [])[0:3].lower()
                        month = MONTH_TO_NUMBER[month_name]
                    else:
                        month = self._detag(d.month, [])
                    if month < 10:
                        month = "0" + str(month)
                    else:
                        month = str(month)
                    pubdate = month + pubdate
            except Exception, errrr:
                pass
            else:
                if (a == 'print' or b == 'ppub'):
                    base_metadata['pubdate'] = pubdate
                elif (a == 'electronic' or b == 'epub'):
                    try:
                        base_metadata['pubdate']
                    except Exception, err:
                        base_metadata['pubdate'] = pubdate
            try:
                if (b == 'open-access'):
                    base_metadata.setdefault('properties', {}).setdefault('OPEN', 1)
            except Exception, err:
                pass

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
        if back_meta is not None:

            ref_list_text = []
            try:
                ref_results = back_meta.find('ref-list').find_all('ref')
                for r in ref_results:
                    s = unicode(r.extract()).replace('\n', '')
                    s = re.sub(r'\s+',r' ',s)
                    s = namedentities.named_entities(s)
                    ref_list_text.append(s)
            except Exception, err:
                pass
            else:
                base_metadata['refhandler_list'] = ref_list_text

        output_metadata = base_metadata

# Last step: entity conversion
        ec_fields = ['authors', 'abstract', 'title']
        econv = EntityConverter()
        for ecf in ec_fields:
            try:
                econv.input_text = output_metadata[ecf]
                econv.convert()
                output_metadata[ecf] = econv.output_text
            except Exception, err:
                pass

        return output_metadata
