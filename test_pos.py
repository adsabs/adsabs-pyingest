
#!/usr/bin/env python

from argparse import ArgumentParser
import urllib
from pyingest.parsers.default import BaseBeautifulSoupParser

class PoSParser(BaseBeautifulSoupParser):

    def __init__(self):
        pass

    def resource_dict(self, fp, **kwargs):
        d = self.bsfiletodict(fp, **kwargs)
        return d


ap = ArgumentParser(description='Process a PoS URL')
ap.add_argument('url', nargs='?', help='URL for the conference')

args = ap.parse_args()
if not args.url:
    quit()
else:
    url = args.url






documents = [{}]

buffer = urllib.urlopen(url)
parser = BaseBeautifulSoupParser()
data = parser.bsfiletodict(buffer)


# Title:
title = data.head.title.get_text()

body = data.body

# Abstract:
abstract = body.find("div", {"id":"abstract"}).get_text().replace('\r','').lstrip().rstrip()

conf_info  = body.find_all("DIV")
dstring = "conference_date>"
for c in conf_info:
    if dstring in c.get_text():
        for x in c.find_all("BR"):
            x.replaceWith(". ")
# Pubdate:
        pubdate = "00/" + c.get_text().split()[2]
# Publication:
        publication = title + ". " + c.get_text().replace(dstring,'').replace(' .','.')

documents.append({'title':title,'abstract':abstract,'pubdate':pubdate,'publication':publication})


papers = body.find_all('td')

for p in papers:
    article = {}
    title = p.find("span", {"class":"contrib_title"})
    pdf = p.find("span", {"class":"contrib_file"})
    auths = p.find("span", {"class":"contrib_authors"})
    if not isinstance(title,type(None)):
# Title:
        article['title'] = title.get_text()
    if not isinstance(auths,type(None)):
# Authors:
        article['authors'] = [auths.get_text()]
    if not isinstance(pdf,type(None)):
        url = pdf.a["href"]
# Page:
        article['page'] = str(int(url.split('/')[2]))

# Properties (PDF URL):
        url = 'https://pos.sissa.it' + url
        article['properties'] = {'PDF':url}

    if article != dict():
        documents.append(article)



for d in documents:
    print(d)
