#!/usr/bin/env python

# arxiv_dc: parser for arXiv records in Dublin Core XML format
# M. Templeton, 2017 November 16

import codecs
from dubcore import DublinCoreParser

class ArxivParser(DublinCoreParser):


    def parse(self, fp, **kwargs):

        r = super(self.__class__, self).parse(fp, **kwargs)

        arx = dict()

        arx['abstract'] = r['descriptions'][0]

        arx['title']    = r['titles'][-1]

        arx['comments'] = " ".join(r['descriptions'][1:])

        arx['authors']  = "; ".join(r['creators'])

        arx['url'],arx['doi'] = make_extras(r['identifiers'])

        arx['bibcode']  = make_bibcode(arx['url'],arx['authors'])

        return arx


def make_extras(ids):
    for x in ids:
        if u'http' in x:
            url = x
        if u'doi' in x:
            doi = x

    return url,doi


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
    if u'[0-9]' in arxiv_id1:
        bibcode = year+'arXiv'+arxiv_id1+arxiv_id2+auth_init
    else:
        bibcode1 = year+arxiv_id1
        bibcode2 = arxiv_id2+auth_init
        bibcodex = u'.'*(19-len(bibcode1)-len(bibcode2))
        bibcode  = bibcode1 + bibcodex + bibcode2

    return bibcode


if __name__ == "__main__":

    arxiv = ArxivParser()
    with open('0306266','rU') as fp:
        x = arxiv.parse(fp)
        for k in x.keys():
            print "%s:\t%s"%(k,x[k])
