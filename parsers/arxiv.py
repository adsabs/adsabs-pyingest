#!/usr/bin/env python

# arxiv_dc: parser for arXiv records in Dublin Core XML format
# M. Templeton, 2017 November 16

import codecs
from dubcore import DublinCoreParser

class ArxivParser(DublinCoreParser):

    def get_abstract(self, r):
        try:
            r['descriptions']
        except KeyError:
            abstract = None
        else:
            abstract = r['descriptions'][0]
        return abstract


    def get_comments(self, r):
        try:
            r['descriptions']
        except KeyError:
            comments = None
        else:
            comments = "\n".join(r['descriptions'][1:])
        return comments


    def get_arxiv_url(self, r):
        try:
            r['identifiers']
        except KeyError:
            arxiv_url = None
        else:
            arxiv_url = r['identifiers'][0]
        return arxiv_url
        
    def parse(self, fp, **kwargs):
        doc = super(self.__class__, self).parse(fp, **kwargs)
        return doc
#       arxiv_record = {
#           }
#       return arxiv_record

if __name__ == "__main__":

    arxiv = ArxivParser()
    with open('oai_ArXiv.org_1711_05739','rU') as fp:
        print arxiv.parse(fp)
