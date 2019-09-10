#!/usr/bin/env python
from default import BaseRSSFeedParser
import urlparse
import sys
import re


class ATelParser(BaseRSSFeedParser):

    def extract_data(self, entry):
        rec = {}
        links={}
        # Journal string template
        journal = "The Astronomer's Telegram, No. %s"
        # Start gathering the necessary fields
        title = entry.find('title').text
        # Telegram number
        telegram = entry.find('identifier').text
        telegram_nr = telegram.upper().replace('ATEL','').strip()
        # Author
        author = entry.find('author').text
        author = re.sub('\ \ +',' ',author).strip()
        author = re.sub(',$','', author)
        # Abstracts
        try:
            abstract = entry.find('description').text
            abstract = re.sub('\ \ +',' ',abstract)
        except:
            abstract = ''
        # Subjects (keywords)
        subjects = entry.find('subjects').text
        # Publication date
        date = entry.find('dc:date').text
        pyear = date.split('-')[0]
        pmnth = date.split('-')[1]
        # Telegram URL
        link = 'http://www.astronomerstelegram.org/?read=%s' % telegram_nr
        links['ELECTR'] = link
        # Construct bibcode
        if int(telegram_nr) < 10000:
                bibcode = '%sATel.%s....1%s' % (pyear,telegram_nr,author.strip()[0])
        else:
                bibcode = '%sATel%s....1%s' % (pyear,telegram_nr,author.strip()[0]) 
        rec = {
            'bibcode': bibcode,
            'title': title,
            'authors': author,
            'properties': links,
            'keywords': subjects.strip(),
            'pubdate': "%s/%s"%(date.split('-')[1],date.split('-')[0]),
            'publication': journal % telegram_nr,
            'abstract': abstract.strip()
        }
        return rec

    def parse(self, url, **kwargs):
        atel_recs = [{}]
        headers = {
                'Content-type': 'text/xml',
                'Accept': 'text/html,application/xhtml+xml,application/xml',
                'User-agent': 'Mozilla/5.0'
            }
        data = self.get_records(url, headers=headers, **kwargs)
        for d in data:
            try:
                atel_recs.append(self.extract_data(d))
            except Exception, err:
                sys.stderr.write('Failed to process record %s (%s). Skipping...\n'%(d.find('identifier').text, err))
                continue


        return atel_recs
