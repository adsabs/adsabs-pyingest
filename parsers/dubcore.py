#!/usr/bin/env python

import sys
import json
import codecs
from default import BaseXmlToDictParser

class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass


class DublinCoreParser(BaseXmlToDictParser):

    def __init__(self):
    # make sure we are utf-8 clean on stdout, stderr
        self.DUBC_SCHEMA = "http://www.openarchives.org/OAI/2.0/oai_dc/"


    def get_schema(self, r):
        schema = []
        for s in self._array(r[u'@xmlns:oai_dc']):
            schema.append(self._text(s))
        if len(schema) == 0:
            raise NoSchemaException("Unknown record schema.")
            schema = None
        elif schema[0] != self.DUBC_SCHEMA:
            raise WrongSchemaException("Wrong schema.")
        else:
            pass
        schema = ['dc:contributor','dc:coverage','dc:creator','dc:date',
                  'dc:description','dc:format','dc:identifier','dc:language',
                  'dc:publisher','dc:relation','dc:rights','dc:source',
                  'dc:subject','dc:title','dc:type']
        return schema


    def get_tag(self, r, tag):
        value = []
        try:
            tag,self._array(r.get(tag,[]))
        except KeyError:
            pass
        else:
            for s in self._array(r.get(tag,[])):
                value.append(self._text(s))
            if len(value) == 0:
                value = None
        return value


    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
        r = d.get('record',{}).get('metadata',{}).get('oai_dc:dc',{})
        return r


    def parse(self, fp, **kwargs):

        output_metadata=dict()

        try:
            r = self.resource_dict(fp, **kwargs)
        except:
            print "Could not parse file into a dictionary."
        else:
            schema = self.get_schema(r)


            for tag in schema:
                if (self.get_tag(r, tag)):
                    output_metadata[tag]=self.get_tag(r, tag)

        return output_metadata



if __name__ == "__main__":

    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    dcx = DublinCoreParser()

    woo = None
    with open('../test/arxiv.test/oai_ArXiv.org_1711_05739','rU') as fp:
        woo = dcx.parse(fp)

    print woo
