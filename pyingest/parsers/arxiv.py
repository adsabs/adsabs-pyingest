#!/usr/bin/env python

# arxiv_dc: parser for arXiv records in Dublin Core XML format
# M. Templeton, 2017 November 16

import codecs
from dubcore import DublinCoreParser

class MissingAuthorException(Exception):
    pass

class MissingTitleException(Exception):
    pass

class MissingAbstractException(Exception):
    pass

class MissingIDException(Exception):
    pass

class MissingDateException(Exception):
    pass

class EmptyParserException(Exception):
    pass

class ArxivParser(DublinCoreParser):


    def parse(self, fp, **kwargs):

        arx = dict()

        print(self.__class__, self)

        r = super(self.__class__, self).parse(fp, **kwargs)

        if(len(r.keys()) == 0):
            raise EmptyParserException("No dictionary.")

        try:
            arx['pubdate']  = r['dc:date'][-1]
        except KeyError:
            raise MissingDateException("Invalid record: no pubdate")
        else:
            pass

        try:
            arx['abstract'] = r['dc:description'][0]
        except KeyError:
            raise MissingAbstractException("Invalid record: no abstract")
        else:
            pass

        try:
            arx['title']    = [r['dc:title'][-1]]
        except KeyError:
            raise MissingTitleException("Invalid record: no title")
        else:
            pass

        try:
            arx['author']  = r['dc:creator']
        except KeyError:
            raise MissingAuthorException("Invalid record: no author(s)")
        else:
            pass

        try:
            arx['keyword'] = r['dc:subject']
        except KeyError:
            raise MissingAbstractException("Invalid record: no subjects")
        else:
            pass

        try:
            arx['lolbutts'] = r['identifier']
        except KeyError:
            pass
        else:
            print ("haha:",arx['lolbutts'])

        try:
            make_extras(r['dc:identifier'])
        except KeyError:
            raise MissingIDException("Invalid record: no identifier")
        else:
            testdoi, url = make_extras(r['dc:identifier'])
            if testdoi != [None]:
                arx['doi'] = testdoi

        try:
            arx['bibcode'] = make_bibcode(url,arx['author'])
        except KeyError:
            raise MissingBibcodeException("Invalid record: cant generate bibcode")
        else:
            pass

        return arx


def make_extras(ids):
    doi = None
    url = None
    for x in ids:
        if u'doi:' in x:
            doi = x
        if u'http' in x:
            if u'arxiv.org' in x:
                url = x

    return [doi],url


def make_bibcode(url,authors):
    (arxiv_id1,arxiv_id2) = url.split('/')[-2:]
    if arxiv_id1 == u'abs':
        (arxiv_id1,arxiv_id2) = arxiv_id2.split('.')
        yy = arxiv_id1[0:2]
    else:
        yy = arxiv_id2[0:2]
        arxiv_id2=arxiv_id2[2:]
        if(arxiv_id2[0] == u'0'):
            arxiv_id2 = arxiv_id2[1:]
    if int(yy) > 90:
        year=u'19'+yy
    else:
        year=u'20'+yy

    if len(arxiv_id2) == 4:
        arxiv_id2 = u'.'+arxiv_id2

    auth_init = authors[0][0]
    if arxiv_id1.isdigit() == True:
        bibcode = year+'arXiv'+arxiv_id1+arxiv_id2+auth_init
    else:
        bibcode1 = year+arxiv_id1
        bibcode2 = arxiv_id2+auth_init
        bibcodex = u'.'*(19-len(bibcode1)-len(bibcode2))
        bibcode  = bibcode1 + bibcodex + bibcode2

    return bibcode


if __name__ == '__main__':

    lol = ArxivParser()

    woo = None
    with open('/proj/ads/abstracts/sources/ArXiv/oai/arXiv.org/astro-ph/9501013','rU') as fp:
        woo = lol.parse(fp)

    print(woo)
