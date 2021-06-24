#!/usr/bin/env python

from __future__ import absolute_import
# import bs4
from bs4 import BeautifulSoup, CData, Tag
from collections import OrderedDict
from .default import BaseBeautifulSoupParser
from .jats_contrib import JATSContribs
from pyingest.config.config import *
from .affils import AffiliationParser
from .entity_convert import EntityConverter
# from uat_key2uri import UATURIConverter
import namedentities
import re
import copy
import sys

if sys.version_info > (3,):
    str_type = str
else:
    str_type = unicode

fix_ampersand = re.compile(r"(&amp;)(.*?)(;)")


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

        newr = BeautifulSoup(str_type(r), 'lxml')
        try:
            tag_list = list(set([x.name for x in newr.find_all()]))
        except Exception as err:
            tag_list = []
        for t in tag_list:
            elements = newr.findAll(t)
            for e in elements:
                if t in JATS_TAGS_DANGER:
                    e.decompose()
                elif t in tags_keep:
                    e.contents
                else:
                    if t.lower() == 'sc':
                        e.string = e.string.upper()
                    e.unwrap()

        # Note: newr is converted from a bs4 object to unicode here.
        # Everything after this point is string manipulation.

        newr = str_type(newr)

        # amp_pat = r'(&amp;)(.*?)(;)'
        amp_fix = fix_ampersand.findall(newr)
        for s in amp_fix:
            s_old = ''.join(s)
            s_new = '&' + s[1] + ';'
            newr = newr.replace(s_old, s_new)

        newr = newr.replace(u'\n', u' ').replace(u'  ', u' ')
        newr = newr.replace('&nbsp;', ' ')

        return newr

    def resource_dict(self, input_data, **kwargs):
        d = self.bsstrtodict(input_data, 'lxml-xml', **kwargs)
        r = d.article
        return r

    def parse(self, input_data, **kwargs):

        output_metadata = {}

        document = self.resource_dict(input_data, **kwargs)

        r = document.front

        try:
            article_meta = r.find('article-meta')
            journal_meta = r.find('journal-meta')
        except Exception as err:
            return {}

        back_meta = document.back

        base_metadata = {}

        # Title:
        title_xref_list = []
        title_fn_list = []
        titledoi = None
        try:
            title = article_meta.find('title-group').find('article-title')
        except Exception as err:
            pass
        else:
            try:
                for dx in title.find_all('ext-link'):
                    titledoi = dx['xlink:href']
            except Exception as err:
                pass
            try:
                for dx in title.find_all('xref'):
                    title_xref_list.append(self._detag(dx, JATS_TAGSET['abstract']).strip())
                    dx.decompose()
                # title.xref.decompose()
                # title.xref.extract()
            except Exception as err:
                pass
            try:
                for df in title.find_all('fn'):
                    title_fn_list.append(self._detag(df, JATS_TAGSET['abstract']).strip())
                    df.decompose()
                # title.fn.decompose()
                # title.fn.extract()
            except Exception as err:
                pass
            base_metadata['title'] = (
                self._detag(title, JATS_TAGSET['title']).strip())

        # Abstract:
        try:
            abstract = article_meta.abstract.p
        except Exception as err:
            pass
        else:
            abstract = (self._detag(abstract, JATS_TAGSET['abstract']))
            base_metadata['abstract'] = abstract
            if title_fn_list:
                base_metadata['abstract'] += '  ' + ' '.join(title_fn_list)

        # Authors and their Affiliations:
        try:
            auth_affil = JATSContribs(soup=article_meta)
            auth_affil.parse()
            aa_output = auth_affil.output
        except Exception as err:
            pass
        else:
            base_metadata['authors'] = '; '.join(aa_output['authors'])
            base_metadata['affiliations'] = aa_output['affiliations']

        # Copyright:
        try:
            copyright = article_meta.find('copyright-statement')
        except Exception as err:
            pass
        else:
            base_metadata['copyright'] = self._detag(copyright, [])

        # Keywords:
        isErratum = False
        try:
            keys_uat = []
            keys_misc = []
            keys_aas = []
            uatkeys = []
            keywords = []
            keyword_groups = article_meta.find_all('kwd-group')
            for kg in keyword_groups:
                # Check for UAT first:
                if kg['kwd-group-type'] == 'author':
                    keys_uat_test = kg.find_all('compound-kwd-part')
                    for kk in keys_uat_test:
                        if kk['content-type'] == 'uat-code':
                            keys_uat.append(self._detag(kk, JATS_TAGSET['keywords']))
                    if not keys_uat:
                        keys_misc_test = kg.find_all('kwd')
                        for kk in keys_misc_test:
                            keys_misc.append(self._detag(kk, JATS_TAGSET['keywords']))
                # Then check for AAS:
                elif kg['kwd-group-type'] == 'AAS':
                    keys_aas_test = kg.find_all('kwd')
                    for kk in keys_aas_test:
                        keys_aas.append(self._detag(kk, JATS_TAGSET['keywords']))
                # If all else fails, just search for 'kwd'
                else:
                    keys_misc_test = kg.find_all('kwd')
                    for kk in keys_misc_test:
                        keys_misc.append(self._detag(kk, JATS_TAGSET['keywords']))

            if keys_uat:
                uatkeys = keys_uat
            if uatkeys:
                base_metadata['uatkeys'] = ', '.join(uatkeys)

            if keys_aas:
                keywords = keys_aas
            if keys_misc:
                if keywords:
                    keywords.extend(keys_misc)
                else:
                    keywords = keys_misc
            if keywords:
                base_metadata['keywords'] = ', '.join(keywords)
        except Exception as err:
            pass

        if 'keywords' not in base_metadata:
            try:
                keywords = article_meta.find('article-categories').find_all('subj-group')
            except Exception as err:
                keywords = []
            for c in keywords:
                try:
                    if c['subj-group-type'] == 'toc-minor':
                        klist = []
                        for k in c.find_all('subject'):
                            klist.append(self._detag(k, JATS_TAGSET['keywords']))
                        base_metadata['keywords'] = ', '.join(klist)
                    else:
                        for k in c.find_all('subject'):
                            if k.string == 'Errata' or k.string == 'Corrigendum':
                                isErratum = True
                except Exception as err:
                    pass

        # No longer required:
        # Now convert any UAT keywords to their URI:
        # try:
            # uat_cnv = UATURIConverter()
            # base_metadata['uatkeys'] = uat_cnv.convert_to_uri(base_metadata['uatkeys'])
        # except Exception as err:
            # pass
        

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
        except Exception as err:
            try:
                journal = journal_meta.find('journal-title')
                base_metadata['publication'] = self._detag(journal, [])
            except Exception as err:
                pass

        try:
            jid = journal_meta.find('journal-id', {'journal-id-type': 'publisher-id'})
            if jid:
                base_metadata['pub-id'] = self._detag(jid, [])
            else:
                try:
                    jid = journal_meta.find('journal-id', {'journal-id-type': 'coden'})
                    if jid:
                        base_metadata['coden'] = self._detag(jid, [])
                except Exception as err:
                    pass
        except Exception as err:
            pass

        # Related article data, especially corrections and errata
        relateddoi = None
        try:
            related = article_meta.find_all('related-article')
            for r in related:
                if r['related-article-type'] == 'corrected-article':
                    isErratum = True
                    relateddoi = r['xlink:href']
        except Exception as err:
            pass

        # links: DOI and arxiv preprints
        # DOI
        base_metadata['properties'] = {}
        if isErratum:
            try:
                doiurl_pat = r'(.*?)(doi.org\/)'
                if titledoi:
                    base_metadata['properties']['ERRATUM'] = re.sub(doiurl_pat, '', titledoi)
                elif relateddoi:
                    base_metadata['properties']['ERRATUM'] = re.sub(doiurl_pat, '', relateddoi)
                else:
                    print('warning, no doi for erratum!')
                    # pass
            except Exception as err:
                print('warning, problem making erratum: %s' % err)
                # pass
        try:
            ids = article_meta.find_all('article-id')
        except Exception as err:
            ids = []
        for d in ids:
            if d['pub-id-type'] == 'doi':
                base_metadata['properties']['DOI'] = self._detag(d, [])
        # Arxiv Preprint
        try:
            arxiv = article_meta.find_all('custom-meta')
        except Exception as err:
            pass
        else:
            ax_pref = 'https://arxiv.org/abs/'
            for ax in arxiv:
                try:
                    x_name = self._detag(ax.find('meta-name'), [])
                    x_value = self._detag(ax.find('meta-value'), [])
                    if x_name == 'arxivppt':
                        base_metadata['properties']['HTML'] = ax_pref + x_value
                except Exception as err:
                    pass

        # Pubdate:
        try:
            pub_dates = article_meta.find_all('pub-date')
        except Exception as err:
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
                except Exception as err:
                    pubdate = "00" + pubdate
                else:
                    try:
                        int(self._detag(d.month, []))
                    except Exception as errrr:
                        month_name = self._detag(d.month, [])[0:3].lower()
                        month = MONTH_TO_NUMBER[month_name]
                    else:
                        month = self._detag(d.month, [])
                    if int(month) < 10:
                        month = "0" + str(int(month))
                    else:
                        month = str(month)
                    pubdate = month + pubdate
            except Exception as errrr:
                pass
            else:
                if a == 'print' or b == 'ppub' or b == 'cover':
                    base_metadata['pubdate'] = pubdate
                elif a == 'electronic' or b == 'epub':
                    try:
                        base_metadata['pubdate']
                    except Exception as err:
                        base_metadata['pubdate'] = pubdate
            try:
                if b == 'open-access':
                    base_metadata.setdefault('properties', {}).setdefault('OPEN', 1)
            except Exception as err:
                pass

        # Check for open-access / "Permissions" field
        try:
            permissions = article_meta.find('permissions').find_all('license')
        except Exception as err:
            pass
        else:
            for p in permissions:
                try:
                    if p['license-type'] == 'open':
                        base_metadata.setdefault('properties', {}).setdefault('OPEN', 1)
                except Exception as err:
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

        # Number of Pages:
        try:
            counts = article_meta.counts
            pagecount = counts.find('page-count')
            base_metadata['numpages'] = '<NUMPAGES>' + pagecount['count'] + '</NUMPAGES>'
        except Exception as err:
            pass

        # References (now using back_meta):
        if back_meta is not None:

            ref_list_text = []
            try:
                ref_results = back_meta.find('ref-list').find_all('ref')
                for r in ref_results:
                    s = str_type(r.extract()).replace('\n', '')
                    s = re.sub(r'\s+', r' ', s)
                    s = namedentities.named_entities(s)
                    ref_list_text.append(s)
            except Exception as err:
                pass
            else:
                base_metadata['refhandler_list'] = ref_list_text

        # Entity Conversions:
        econv = EntityConverter()
        for k, v in base_metadata.items():
            if isinstance(v,str_type):
                econv.input_text = v
                econv.convert()
                v = econv.output_text
            elif isinstance(v, list):
                newv = []
                for l in v:
                    if isinstance(l,str_type):
                        econv.input_text = l
                        econv.convert()
                        l = econv.output_text
                    newv.append(l)
                v = newv
            else:
                pass
            output_metadata[k] = v


        return output_metadata
