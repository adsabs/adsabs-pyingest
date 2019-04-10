#!/usr/bin/env python

# arxiv_dc: parser for arXiv records in Dublin Core XML format
# M. Templeton, 2017 November 16

import codecs
from dubcore import DublinCoreParser
import ads_nameparser
from adsputils import u2asc
from xml.parsers import expat


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
        output = u2asc(namestring)
        for c in output:
            if c.isalpha():
                return c.upper()
        return u'.'


    def parse(self, fp, **kwargs):

        arx = dict()

        try:
            r = super(self.__class__, self).parse(fp, **kwargs)
        except expat.ExpatError:
            raise EmptyParserException("Not parseable xml")
        else:
            pass

        if r['abstract']:
            r['comments']=[x.replace('Comment:','').strip() for x in r['abstract'][1:]]
            r['abstract']=r['abstract'][0]

        if r['authors']:
            try:
                reparsed_name = ads_nameparser.ads_name_adjust(r['authors'])
            except exception as e:
                print("Error in arxiv name parsing: ",e)
            else:
                r['authors'] = reparsed_name

        if r['bibcode']:
            idarray = r['bibcode'].split(':')
            arxiv_id = idarray[-1]

            r['publication'] = 'eprint arXiv:'+arxiv_id

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
                n1 = arx_num[0:4]
                n2 = arx_num[4:]
                if len(n2) < 5:
                    arx_num = n1 + u'.' + n2
                else:
                    arx_num = n1 + n2
                arx_yy = arx_num[0:2]

            if int(arx_yy) > 90:
                year=u'19'+arx_yy
            else:
                year=u'20'+arx_yy

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
            prop = {}
            pubnote_prop = []
            for x in r['properties']:
                if 'http://arxiv.org' in x:
                    prop['HTML'] = x
                else:
                    if 'doi:' in x:
                        prop['DOI'] = x
                    pubnote_prop.append(x)
            r['properties'] = prop

            if r['comments']:
                if len(pubnote_prop) > 0:
                    r['comments'] = r['comments'] + pubnote_prop

        return r
#
#if __name__ == '__main__':
#
#    import glob
#
#    test = ArxivParser()
#
#    fl = []
#    meta_dir='/proj/ads/abstracts/sources/ArXiv/oai/arXiv.org/'
#
## old style, pre-07 astro-ph:
#    fl.append(meta_dir+'astro-ph/9501013')
#
## old style, pre-07 non astro-ph:
#    fl.append(meta_dir+'math/0306266')
#
## new style, with a unicode (&#hhh;) as first author initial:
#    fl.append(meta_dir+'0901/2443')
#
## Gerard 't Hooft... regardless of what classic has, arxiv meta is "Hooft, Gerard 't" in every case I checked.
#    fl.append(meta_dir+'hep-th/0408148')
#    fl.append(meta_dir+'1709/02874')
#
## old style, weird case where arxiv meta is fine, but classic parsed it weirdly:
#    fl.append(meta_dir+'cond-mat/9706161')
#
## new style, random tests:
#    fl.append(meta_dir+'1711/04702')
#    fl.append(meta_dir+'1711/05739')
#    fl.append(meta_dir+'1807/03779')
#
#
#    for f in fl:
#        with open(f,'rU') as fp:
#            woo = test.parse(fp)
#            print(woo)
#            print("\n\n\n")
