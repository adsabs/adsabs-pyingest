#!/usr/bin/env python

import sys
import json
import codecs
from default import BaseXmlToDictParser

class WrongSchemaException(Exception):
    pass

class MissingHeaderException(Exception):
    pass

class MissingTextException(Exception):
    pass

class MissingAuthorsException(Exception):
    pass

class MissingTitleException(Exception):
    pass


class DublinCoreParser(BaseXmlToDictParser):

    def __init__(self):
    # make sure we are utf-8 clean on stdout, stderr
        self.DUBC_SCHEMA = "http://www.openarchives.org/OAI/2.0/oai_dc/"


# This should have all of the possible fields of Dublin Core specification
# as specified in http://www.openarchives.org/OAI/2.0/oai_dc/

# You know, you should refactor this to have one "def" that gets its
# possible assignment names from resource_dict, rather than specifying
# everything beforehand.  That way you're 100% compliant with what's in
# the document -- except each document may not have the full set of 
# possible keys, and you want to handle cases where those keys have data
# type None gracefully.... Maybe define a "dc_dict" as well as a record
# dependent resource_dict?

    def get_description(self, r):
        descrip = []
        for s in self._array(r.get('dc:description',[])):
            descrip.append(self._text(s))
        if len(descrip) == 0:
            descrip = None
        return descrip


    def get_creator(self, r):
        creator = []
        for s in self._array(r.get('dc:creator',[])):
            creator.append(self._text(s))
        if len(creator) == 0:
            raise MissingAuthorsException("No authors found")
            creator = None
        return creator


    def get_title(self, r):
        title = []
        for s in self._array(r.get('dc:title',[])):
            title.append(self._text(s))
        if len(title) == 0:
            raise MissingTitleException("No title found")
            title = None
        return title


    def get_identifier(self, r):
        identifier = []
        for s in self._array(r.get('dc:identifier',[])):
            identifier.append(self._text(s))
        if len(identifier) == 0:
            identifier = None
        return identifier


    def get_subject(self, r):
        subject = []
        for s in self._array(r.get('dc:subject',[])):
            subject.append(self._text(s))
        if len(subject) == 0:
            subject = None
        return subject


    def get_date(self, r):
        date = []
        for s in self._array(r.get('dc:date',[])):
            date.append(self._text(s))
        if len(date) == 0:
            date = None
        return date


    def get_doctype(self, r):
        doctype = []
        for s in self._array(r.get('dc:type',[])):
            doctype.append(self._text(s))
        if len(doctype) == 0:
            doctype = None
        return doctype


    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
        r = d.get('record',{}).get('metadata',{}).get('oai_dc:dc',{})
        return r


    def parse(self, fp, **kwargs):

        r = self.resource_dict(fp, **kwargs)
#       print ("lol, remove me: ",r.keys())

        creators = self.get_creator(r)
        identifiers = self.get_identifier(r)
        titles = self.get_title(r)
        descriptions = self.get_description(r)
        subjects = self.get_subject(r)
        dates = self.get_date(r)
        doctypes = self.get_doctype(r)

        return {
            'creators': creators,
            'titles': titles,
            'identifiers': identifiers,
            'descriptions': descriptions,
            'subjects': subjects,
            'dates': dates,
            'doctypes': doctypes
            }
            

if __name__ == "__main__":

    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    dcx = DublinCoreParser()

    woo = None
    with open('test/oai_ArXiv.org_1711_05739','rU') as fp:
        woo = dcx.parse(fp)

    print woo
