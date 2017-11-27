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

class ArxivParser(DublinCoreParser):


    def parse(self, fp, **kwargs):

        r = super(self.__class__, self).parse(fp, **kwargs)

        arx = dict()

        try:
            arx['pubdate']  = r['dc:date'][-1]
        except KeyError:
            raise MissingDateException("Invalid record: no pubdate")
        else:
            arx['pubhist']  = r['dc:date'][0:-1]
            if(len(arx['pubhist']) == 0):
                arx['pubhist'] = None

        try:
            arx['abstract'] = r['dc:description'][0]
        except KeyError:
            raise MissingAbstractException("Invalid record: no abstract")
        else:
            arx['comments'] = " ".join(r['dc:description'][1:])

        try:
            arx['title']    = r['dc:title'][-1]
        except KeyError:
            raise MissingTitleException("Invalid record: no title")
        else:
            pass

        try:
            arx['authors']  = "; ".join(r['dc:creator'])
        except KeyError:
            raise MissingAuthorException("Invalid record: no author(s)")
        else:
            pass

        try:
            arx['subjects'] = ", ".join(r['dc:subject'])
        except KeyError:
            raise MissingAbstractException("Invalid record: no subjects")
        else:
            pass

        try:
            make_extras(r['dc:identifier'])
        except KeyError:
            raise MissingIDException("Invalid record: no identifier")
        else:
            arx['doi'],arx['url'] = make_extras(r['dc:identifier'])

        arx['bibcode']  = make_bibcode(arx['url'],arx['authors'])

        return arx


def make_extras(ids):
    doi = None
    url = None
    for x in ids:
        if u'doi' in x:
            doi = x
        if u'http' in x:
            url = x

    return doi,url


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
    if int(arxiv_id1) > 0:
        bibcode = year+'arXiv'+arxiv_id1+arxiv_id2+auth_init
    else:
        bibcode1 = year+arxiv_id1
        bibcode2 = arxiv_id2+auth_init
        bibcodex = u'.'*(19-len(bibcode1)-len(bibcode2))
        bibcode  = bibcode1 + bibcodex + bibcode2

    return bibcode


if __name__ == "__main__":

    arxiv = ArxivParser()
    with open('../test/arxiv.test/oai_ArXiv.org_1711_05739','rU') as fp:
        x = arxiv.parse(fp)
        for k in x.keys():
            print "%s:\t%s"%(k,x[k])
