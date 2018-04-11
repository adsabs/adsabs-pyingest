#!/usr/bin/env python

import sys
import json
import codecs
from adsputils import u2asc
from default import BaseXmlToDictParser

class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass

class UnparseableException(Exception):
    pass

class JATSParser(BaseXmlToDictParser):

    def __init__(self):
    # make sure we are utf-8 clean on stdout, stderr
        self.JATS_SCHEMA = ""

    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
# this returns the root of a JATS article, which is the element <article>
        r = d.get('article',{})
        return r

    def _attribs(self, r, **kwargs):
        kl = self._dict(r).keys()
        attribs = {}
        for k in kl:
            if k[0] == '@':
                attribs[k] = r[k]
        return attribs

    def parse(self, fp, **kwargs):

        output_metadata=dict()

        r = self.resource_dict(fp, **kwargs)

        article_attr = self._attribs(r)
        front_meta = r.get('front')
        back_meta = r.get('back')

        try:
            front_keys, back_keys = (front_meta.keys(),back_meta.keys())
        except AttributeError:
            return
        else:
            article_meta = front_meta.get('article-meta')
            journal_meta = front_meta.get('journal-meta')
            try:
                article_keys, journal_keys = (article_meta.keys(),back_meta.keys())
            except AttributeError:
                return
            else:

# Title
                try:
                    output_metadata['title'] = article_meta['title-group']['article-title']
                except KeyError:
                    pass

# Abstract
                try:
                    output_metadata['abstract'] = article_meta['abstract']['p']
                except KeyError:
                    pass

# Author(s)
                try:
                    output_metadata['authors'] = article_meta['contrib-group']['contrib']
                    for a in output_metadata['authors']:
                        if self._attr(a,'contrib-type') == 'author':
                            print "Author: %s, %s"%(a['name']['surname'],a['name']['given-names'])
                except KeyError:
                    pass

        return output_metadata





if __name__ == "__main__":
 
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
 
    jatsx = JATSParser()
 
    woo = None
    with open('/Users/mtempleton/adsaps.work/fulltext.xml','rU') as fp:
        woo = jatsx.parse(fp)
 
    print(woo)
