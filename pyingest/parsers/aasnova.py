#!/usr/bin/env python
from __future__ import absolute_import
from .default import BaseRSSFeedParser
import sys
import re
import calendar

## AAS Nova tags (to remove from keywords)
AASNova_tags = ['Highlights','Astrobites','Features','Images','AAS News']
## Pattern for categories allowed
re_cats_allowed = re.compile(r'(highlights|astrobites)', re.IGNORECASE) 
## Pattern used to locate references of a doi inside a citation
doi_pattern = r'doi:\s*(?P<doi>10\.\d{4,9}/\S+\w)'
re_doi = re.compile(doi_pattern, re.IGNORECASE)
## Get CDATA contents
# <![CDATA[habitability]]>
re_CDATA = re.compile(r'<!\[CDATA\[(?P<tag>.*?)\]\]>', re.IGNORECASE)
## Convert month name to number
mnth2num = {month.lower(): index for index, month in enumerate(calendar.month_abbr) if month}
## Exceptions
class NoPublicationDateFound(Exception):
    pass

class AASNovaParser(BaseRSSFeedParser):

    def extract_data(self, entry):
        links = {}
        # Get the categories
        try:
            categories = [c.text for c in entry.find_all('category')]
        except:
            categories = []
        check = [c for c in categories if re_cats_allowed.search(c)] 
        # Skip if the entry is not the right category
        if len(check) == 0:
            return {}
        keywords = []
        for c in categories:
            kmat = re_CDATA.search(c)
            if kmat:
                keywords.append(kmat.group('tag'))
        # Remove AAS Nova tags
        keywords = [k for k in keywords if k not in AASNova_tags]
        # Start gathering the necessary fields
        title = entry.find('title').text
        # Get author data
        au = entry.find('dc:creator').text
        amat = re_CDATA.search(au)
        if amat:
            au = amat.group('tag')
        if au.lower() != 'astrobites':
            audata = au.split()
            fname = audata[0]
            lname = " ".join(audata[1:])
            author = "%s, %s" % (lname, fname)
        else:
            author = "Astrobites"
            lname = "Astrobites"
        # Nova record number
        nova_entry = entry.find('guid').text
        links['ELECTR'] = nova_entry
        # The record number follows from the URL:
        # e.g. https://aasnova.org/?p=10858
        # Of course, we can parse the URL using the urllib.parse library
        # but that seems overkill here
        recno = nova_entry.split('p=')[-1]
        # Attempt to find the citation in the record (for the paper
        # discussed in this AAS Nova entry)
        try:
            citation = entry.find('citation').text
        except:
            citation = None
        # If we found a citation, see if we can capture a DOI
        doi = None
        if citation:
            dmat = re_doi.search(citation)
            if dmat:
                doi = dmat.group('doi').strip()
        # Get the publication date
        try:
            pdate = entry.find('pubdate').text.split()
            pubdate = " ".join(pdate[1:4])
            mnth = mnth2num.get(pdate[2].lower(), '00')
            year = pdate[3]
        except:
            raise NoPublicationDateFound("AAS Nova entry does not contain publication date")
        # Get the journal entry
        journal = "AAS Nova Highlight %s, id. %s" % (pubdate, recno)
        # Get the abstract data
        try:
            abstract = entry.find('description').text.replace('<![CDATA[','').replace(']]>','').strip()
            abstract = re.sub('The post.*?appeared first on AAS Nova\.','', abstract).strip()
        except:
            abstract = ''
        # Sometimes the associated DOI(s) are in the 'contents' data, 
        # in case we did not find one earlier
        if not doi:
            contents = entry.find('content:encoded').text
            # We take the first DOI we find
            try:
                doi = re.findall(doi_pattern, contents, re.IGNORECASE)[0]
            except:
                doi = None
        if doi:
            # If we have a DOI, assign it to the ASSOCIATED link
            links['ASSOCIATED'] = "https://dx.doi/%s"%doi
        # Form the bibcode
        bibcode = "%snova.pres%s%s" % (year, recno.rjust(4, '.'), lname[0])
        # Now we have all information to send back
        rec = {
            'bibcode': bibcode,
            'title': title,
            'authors': author,
            'properties': links,
            'keywords': ", ".join(keywords),
            'pubdate': "%s/%s" % (mnth, year),
            'publication': journal,
            'abstract': abstract.strip()
        }
        return rec

    def parse(self, url, **kwargs):
        atel_recs = [{}]
        headers = {
            'Content-type': 'text/xml',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'User-agent': 'Mozilla/5.0'}
        data = self.get_records(url, headers=headers, **kwargs)
        for d in data:
            try:
                atel_recs.append(self.extract_data(d))
            except Exception as err:
                sys.stderr.write('Failed to process record %s (%s). Skipping...\n' % (d.find('identifier').text, err))
                continue

        return atel_recs
