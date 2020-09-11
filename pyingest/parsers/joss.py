#!/usr/bin/env python
from __future__ import absolute_import
from .default import BaseRSSFeedParser
import urlparse
import sys


class JOSSParser(BaseRSSFeedParser):

    def extract_data(self, entry):
        rec = {}
        # By default we put these records in the General database
        # This may be replaced by AST and/or PHY later on
        database = ['GEN']
        # Journal string template
        journal = 'Journal of Open Source Software, vol. %s, issue %s, id. %s'
        # The following keywords are used for comparison with user-supplied
        # keywords for the decision to put a record in the astronomy and/or
        # physics collection
        astro_kw = ['astronomy', 'astrophysics', 'planetary sciences', 'solar physics']
        physics_kw = ['physics', 'engineering']
        # Start gathering the necessary fields
        title = entry.find('title').text
        links = {}
        try:
            doi = entry.find('doi').text
        except Exception as err:
            doi = ''
        try:
            spage = entry.find('page').text
        except Exception as err:
            spage = str(int(doi.split('.')[-1]))
        if len(spage) <= 4:
            pg = spage.rjust(4, '.')
        try:
            volume = entry.find('volume').text
        except Exception as err:
            volume = '0'
        try:
            issue = entry.find('issue').text
        except Exception as err:
            issue = '0'
        try:
            links['DOI'] = doi
        except Exception as err:
            pass
        try:
            links['PDF'] = entry.find('pdf_url').text
        except Exception as err:
            pass
        try:
            links['data'] = entry.find('archive_doi').text
        except Exception as err:
            pass
        # The user-defined tags are used as keywords
        try:
            keywords = entry.find('tags').text.split(',')
        except Exception as err:
            keywords = []
        # Add the programming languages as keywords
        try:
            keywords += entry.find('languages').text.split(',')
        except Exception as err:
            pass
        # strip spaces from keywords
        keywords = [k.strip() for k in keywords]
        # change to database to AST and/or PHY if necessary
        if set([k.lower() for k in keywords]) & set(astro_kw):
            database = ['AST']
        if set([k.lower() for k in keywords]) & set(physics_kw):
            # if GEN is still in the list, remove it:
            # GEN
            try:
                database.remove('GEN')
            except Exception as err:
                pass
            database.append('PHY')

        pubdate = entry.find('published_at').text

        authors = []
        affils = []
        for a in entry.find_all('author'):
            fn = a.find('given_name').text
            ln = a.find('last_name').text
            authors.append("%s, %s" % (ln, fn))
            try:
                aff = a.find('affiliation').text
            except Exception as err:
                aff = ''
            try:
                orcid = a.find('orcid').text
                aff += ' <ID system="ORCID">%s</ID>' % orcid.strip()
            except Exception as err:
                pass
            affils.append(aff.strip())

        try:
            initial = authors[0][0]
        except Exception as err:
            initial = '.'
        bibcode = "%sJOSS.%s.%s%s" % (pubdate[:4], volume.rjust(4, '.'), pg, initial)
        rec = {
            'bibcode': bibcode,
            'title': title,
            'authors': authors,
            'affiliations': affils,
            'properties': links,
            'keywords': list(set([k.strip() for k in keywords])),
            'pubdate': pubdate,
            'page': spage,
            'publication': journal % (volume, issue, spage),
            'database': database
        }

        return rec

    def parse(self, url, **kwargs):
        joss_links = {}
        joss_recs = [{}]
        data = self.get_records(url, **kwargs)
        res = [joss_links.update({l['rel'][0]:l['href']}) for l in self.links if l['rel']]
        for d in data:
            try:
                joss_recs.append(self.extract_data(d))
            except Exception as err:
                sys.stderr.write('Failed to process record %s (%s). Skipping...\n' % (d.find('id').text, err))
                continue

        parsed_path = urlparse.urlparse(joss_links['last'])
        urlparams = urlparse.parse_qs(parsed_path.query, keep_blank_values=1)
        last_page = int(urlparams['page'][0])
        # if last_page equals 1, we're done
        if last_page == 1:
            return joss_recs

        for i in range(2, last_page + 1):
            kwargs['page'] = i
            data += self.get_records(url, **kwargs)
            for d in data:
                try:
                    joss_recs.append(self.extract_data(d))
                except Exception as err:
                    sys.stderr.write('Failed to process record %s (%s). Skipping...\n' % (d.find('id').text, err))
                    continue

        return joss_recs
