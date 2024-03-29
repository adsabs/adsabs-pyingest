#!/usr/bin/env python

from __future__ import absolute_import
from .default import BaseXmlToDictParser


class NoSchemaException(Exception):
    pass


class WrongSchemaException(Exception):
    pass


class UnparseableException(Exception):
    pass


class DublinCoreParser(BaseXmlToDictParser):

    def __init__(self):
        # make sure we are utf-8 clean on stdout, stderr
        self.DUBC_SCHEMA = "http://www.openarchives.org/OAI/2.0/oai_dc/"

    def check_schema(self, r):
        schema_spec = []
        for s in self._array(r[u'@xmlns:oai_dc']):
            schema_spec.append(self._text(s))
        if len(schema_spec) == 0:
            raise NoSchemaException("Unknown record schema.")
        elif schema_spec[0] != self.DUBC_SCHEMA:
            raise WrongSchemaException("Wrong schema.")
        else:
            pass

    def get_tag(self, r, tag):
        value = []
        for s in self._array(r.get(tag, [])):
            value.append(self._text(s))
        if len(value) == 0:
            value = None
        return value

    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
        header = d.get('record', {}).get('header', {})
        r = d.get('record', {}).get('metadata', {}).get('oai_dc:dc', {})
        return header, r

    def make_dubc_bibcode(self, ident):
        return ident

    def parse(self, fp, **kwargs):
        # Note: this generic DC parser may not return an object that has all
        # metadata needed for a tagged record, but not every DC record will
        # have all of that information.

        output_metadata = dict()

        header, r = self.resource_dict(fp, **kwargs)
        try:
            self.check_schema(r)
        except Exception as err:
            raise UnparseableException("Cannot parse record.")
        else:
            # Bibcode
            idtag = header.get('identifier', {})
            if idtag is not None:
                output_metadata['bibcode'] = self.make_dubc_bibcode(idtag)

            # Title
            if self.get_tag(r, 'dc:title'):
                if len(self.get_tag(r, 'dc:title')) == 1:
                    output_metadata['title'] = self.get_tag(r, 'dc:title')[0]
                else:
                    output_metadata['title'] = ": ".join(self.get_tag(r, 'dc:title'))

            # Authors
            if self.get_tag(r, 'dc:creator'):
                if len(self.get_tag(r, 'dc:creator')) == 1:
                    output_metadata['authors'] = self.get_tag(r, 'dc:creator')[0]
                else:
                    output_metadata['authors'] = "; ".join(self.get_tag(r, 'dc:creator'))

            # Pubdate
            if self.get_tag(r, 'dc:date'):
                output_metadata['pubdate'] = self.get_tag(r, 'dc:date')[0]

            # Abstract
            # Note: for generic dublin core, I'm passing all entries tagged
            # with 'dc:description'.  For arXiv.org, it's only
            # r['dc:description'][0]
            if self.get_tag(r, 'dc:description'):
                output_metadata['abstract'] = self.get_tag(r, 'dc:description')

            # Keywords
            if self.get_tag(r, 'dc:subject'):
                if len(self.get_tag(r, 'dc:subject')) == 1:
                    output_metadata['keywords'] = self.get_tag(r, 'dc:subject')[0]
                else:
                    output_metadata['keywords'] = "; ".join(self.get_tag(r, 'dc:subject'))

            # Properties
            # Note: for generic dublin core, I'm passing everything in
            # 'dc:identifier'; for arXiv.org, the one you're interested in is
            # the URL to the arxiv.org abstract page
            if self.get_tag(r, 'dc:identifier'):
                output_metadata['properties'] = self.get_tag(r, 'dc:identifier')

            # specific to arXiv, return arXiv_classes
            if self.get_tag(header, 'setSpec'):
                output_metadata['class'] = self.get_tag(header, 'setSpec')

        return output_metadata
