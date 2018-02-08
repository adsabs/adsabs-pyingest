#!/usr/bin/env python

# arxiv_dc: parser for arXiv records in Dublin Core XML format
# M. Templeton, 2017 November 16

import codecs
from dubcore import DublinCoreParser
from adsputils import u2asc


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

    def get_author_init(self,namestring):
        print ("lol, I am in get_author_init")
        output = u2asc(namestring)
        return output[0]


    def parse(self, fp, **kwargs):

        arx = dict()

        r = super(self.__class__, self).parse(fp, **kwargs)

        if r['abstract']:
            r['abstract']=r['abstract'][0]

        if r['bibcode']:
            idarray = r['bibcode'].split(':')
            arxiv_id = idarray[-1]

            if arxiv_id[0].isalpha():
                arx_field = arxiv_id.split('/')[0].replace('-','.')
                arx_num = arxiv_id.split('/')[1]
                arx_yy = arx_num[0:2]
                if arx_num[2] == '0':
                    arx_num = arx_num[3:]
                else:
                    arx_num = arx_num[2:]
            else:
                arx_field = 'arXiv'
                arx_num = arxiv_id.replace('.','')
                arx_yy = arx_num[0:2]

            if int(arx_yy) > 90:
                year=u'19'+arx_yy
            else:
                year=u'20'+arx_yy

# You're going to need to fix this for non-ascii first initials, but whatevs.
            author_init=self.get_author_init(r['authors'])

            bibcode1 = year+arx_field
            bibcode2 = arx_num+author_init
            if(len(bibcode1)+len(bibcode2) < 19):
                bibcodex = u'.'*(19-len(bibcode1)-len(bibcode2))
                bibcode = bibcode1 + bibcodex + bibcode2
            else:
                bibcode = bibcode1 + bibcode2
            r['bibcode'] = bibcode

        if r['properties']:
            for x in r['properties']:
                if 'http://arxiv.org' in x:
                    r['properties'] = x

        return r

if __name__ == '__main__':

    test = ArxivParser()

    fl = ['/proj/ads/abstracts/sources/ArXiv/oai/arXiv.org/astro-ph/9501013',
          '/proj/ads/abstracts/sources/ArXiv/oai/arXiv.org/math/0306266',
          '/proj/ads/abstracts/sources/ArXiv/oai/arXiv.org/1711/04702',
          '/proj/ads/abstracts/sources/ArXiv/oai/arXiv.org/1711/05739']
    for f in fl:
        with open(f,'rU') as fp:
            woo = test.parse(fp)
            print(woo)
            print("\n\n\n")

