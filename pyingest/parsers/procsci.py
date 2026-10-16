#!/usr/bin/env python

from __future__ import absolute_import
import requests
from .default import BaseBeautifulSoupParser


class URLError(Exception):
    pass


class ContentError(Exception):
    pass


class NotPublishedError(Exception):
    pass


class PoSParser(BaseBeautifulSoupParser):

    # PoSParser will return a list of articles taken from a Proceedings of
    # Science (pos.sissa.it) conference page.  Instead of the typical parser
    # that returns just one record, it will return a TOC-format list where
    # each element in the list can be passed to the serializer (e.g.
    # classic.Tagged())

    def __init__(self):
        pass

    def get_buffer(self, url, **kwargs):
        hostname = url.split('/')[2]
        if hostname != 'pos.sissa.it':
            raise URLError("This parser is only for pos.sissa.it.")
        try:
            pos_buffer = requests.get(url)
        except IOError:
            raise URLError("Could not open from %s" % url)
        return pos_buffer

    def resource_dict(self, fp, **kwargs):
        d = self.bsstrtodict(fp, **kwargs)
        return d

    def parse(self, url, **kwargs):

        pos_toc = [{}]

        data = self.resource_dict(self.get_buffer(url).text)

        # Title:
        title = data.head.title.get_text()

        body = data.body

        if isinstance(body, type(None)):
            raise ContentError("Data from %s is not formatted correctly, check URL." % url)
        else:
            text_message = body.find("div", {"id": "text_message"})
            if not isinstance(text_message, type(None)):
                raise NotPublishedError("The desired volume is not published.")
            else:

                # Abstract:
                abstract = body.find("div", {"id": "abstract"}).get_text().replace('\r', '').replace('\n', '').lstrip().rstrip()

                conf_info = body.find_all("div", {"class": "conference_date"})

                # Pubdate:
                for c in conf_info:
                    for x in c.find_all("br"):
                        x.replaceWith(". ")
                    pubdate_array = c.get_text().split()
                    pubdate = "0000"
                    for item in pubdate_array:
                        if len(item) == 4:
                            try:
                                int(item)
                            except Exception as err:
                                pass
                            else:
                                pubdate = item

                    # Publication:
                    publication = title + ". " + c.get_text().replace(' .', '.')

                pos_toc.append({'title': title, 'abstract': abstract, 'pubdate': pubdate, 'publication': publication})

                papers = body.find_all('td')

                for p in papers:
                    print("YA-BOO: %s" % p)
                    article = {}
                    title = p.find("div", {"class": "contrib_title"})
                    pdf = p.find("div", {"class": "contrib_file"})
                    auths = p.find("div", {"class": "contrib_authors"})
                    page = p.find("div", {"class": "contrib_code"})

                    # Title:
                    if not isinstance(title, type(None)):
                        article['title'] = title.get_text()

                    # Authors:
                    if not isinstance(auths, type(None)):
                        article['authors'] = [auths.get_text()]

                    # Page:
                    if not isinstance(page, type(None)):
                        article['page'] = str(int(page.a["href"].split('/')[2]))

                    # Properties (PDF URL):
                    if not isinstance(pdf, type(None)):
                        if not isinstance(pdf.a, type(None)):
                            url = "https://pos.sissa.it" + pdf.a['href']
                            article['properties'] = {'PDF': url}

                    if article != dict():
                        pos_toc.append(article)

                return pos_toc
