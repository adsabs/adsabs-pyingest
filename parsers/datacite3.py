#!/usr/bin/python
#
#

import sys
import json
import codecs
from default import BaseXmlToDictParser

class WrongSchemaException(Exception):
    pass
class MissingDoiException(Exception):
    pass
class MissingAuthorsException(Exception):
    pass
class MissingTitleException(Exception):
    pass

class DataCite3Parser(BaseXmlToDictParser):

    def __init__(self):
        # make sure we are utf-8 clean on stdout, stderr
        self.DC3_SCHEMA = 'http://datacite.org/schema/kernel-3'
        self.OA_URIS = [ 'info:eu-repo/semantics/openAccess' ]
        self.OA_TEXT = [ 'Open Access' ]

    def get_abstract(self, r):
        # abstract, references are all in the "descriptions" section
        # as of version 3.1 of datacite schema, "References" is not an
        # allowed description type so Lars is shoving the references
        # in a section labeled as "Other" as a json structure
        abstract = None
        for s in self._array(r.get('descriptions',{}).get('description',[])):
            t = s.get('@descriptionType')
            if t == 'Abstract':
                abstract = self._text(s)
        return abstract

    def get_references(self, r):
        # as of version 3.1 of datacite schema, "References" is not an
        # allowed description type but here we try just for kicks
        references = []
        for s in self._array(self._dict(r.get('descriptions')).get('description',[])):
            t = s.get('@descriptionType')
            c = self._text(s)
            if t == 'References':
                # XXX not supported yet, but one can only hope...
                references = c.split('\n')
        return references

    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
        # as a convenience, remove the OAI wrapper if it's there
        r = d.get('record',{}).get('metadata',{}).get('resource') or d.get('resource')
        return r

    def parse(self, fp, **kwargs):
        """
        DataCite 3.1 metadata returns ADS tagged format.
        Note: we use the object's _dict() and _array() functions to guard against
        unexpeected element constructs in the XML (e.g. empty elements or single
        sub-elements when a list is allowed
        """
        r = self.resource_dict(fp, **kwargs)

        # check for namespace to make sure it's datacite3
        schema = r.get('@xmlns')
        if schema != self.DC3_SCHEMA:
            raise WrongSchemaException("Unexpected XML schema \"%s\"" % schema)
    
        if 'DOI' != r.get('identifier',{}).get('@identifierType',''):
            raise MissingDoiException("//identifier['@identifierType'] not DOI!")
        doi = r.get('identifier').get('#text')

        # authors
        authors = []
        aaffils = []
        for a in self._array(self._dict(r.get('creators')).get('creator',[])):
            authors.append(a.get('creatorName'))
            aff = a.get('affiliation','')
            for i in self._array(a.get('nameIdentifier')):
                if 'ORCID' == i.get('@nameIdentifierScheme') or \
                        'http://orcid.org' == i.get('@schemeURI'):
                    aff = aff + ' <ORCID>' + i.get('#text') + '</ORCID>'
            aaffils.append(aff.strip())
        if not authors:
            raise MissingAuthorsException("No authors found for")

        # title
        titles = {}
        for t in self._array(self._dict(r.get('titles')).get('title',[])):
            l = self._attr(t, 'lang', 'en')
            titles[l] = self._text(t)
        if not titles:
            raise MissingTitleException("No title found")
        # we use the english title as the main one
        # then add any foreign ones
        title = titles.pop('en')
        for l in titles:
            title += ' <TITLE lang="%s">%s</TITLE>' % (l, titles[l])

        # publication year and date
        year = self._text(r.get('publicationYear'))
        pubdate = None
        dates = {}
        for d in self._array(self._dict(r.get('dates')).get('date',[])):
            t = self._attr(d, 'dateType')
            dates[t] = self._text(d)
        for dt in [ 'Issued', 'Created', 'Submitted' ]:
            if dt in dates:
                pubdate = dates[dt]
        if not pubdate:
            pubdate = year

        # keywords
        keywords = []
        for k in self._array(self._dict(r.get('subjects')).get('subject',[])):
            # XXX we are ignoring keyword scheme
            keywords.append(self._text(k))

        # contributors (non-authors)
        contribs = []
        caffils = []
        ctypes = []
        for a in self._array(self._dict(r.get('contributors')).get('contributor',[])):
            contribs.append(a.get('contributorName'))
            ctypes.append(a.get('@contributorType',''))
            aff = a.get('affiliation','')
            for i in self._array(a.get('nameIdentifier')):
                if 'ORCID' == i.get('@nameIdentifierScheme') or \
                        'http://orcid.org' == i.get('@schemeURI'):
                    aff = aff + ' <ORCID>' + i.get('#text') + '</ORCID>'
            caffils.append(aff.strip())

        # for now we are ignoring <dates> until it's clear what goes in there...
    
        # we should probably look at what's in '@resourceTypeGeneral'...
        rtype = self._text(r.get('resourceType'))

        # identifiers
        # bibcodes should appear as <alternateIdentifiers>
        identifiers = {}
        bibcode, html, pdf = None, None, None
        for i in self._array(self._dict(r.get('alternateIdentifiers')).get('alternateIdentifier',[])):
            t = i.get('@alternateIdentifierType')
            if t == 'URL':
                html = self._text(i)
            elif t == 'bibcode':
                bibcode = self._text(i)
            else:
                identifiers[t] = self._text(i)

        # related identifiers; bibcodes sometime appear in <relatedIdentifiers>
        for i in self._array(self._dict(r.get('relatedIdentifiers')).get('relatedIdentifier',[])):
            t = i.get('@relatedIdentifierType')
            rt = i.get('@relationType')
            c = self._text(i)
            if t == 'URL' and rt == 'HasPart' and c.endswith('.pdf'):
                pdf = c
            elif t == 'bibcode':
                bibcode = c
            else:
                identifiers[t] = self._text(i)

        # access rights
        isoa = False
        for a in self._array(self._dict(r.get('rightsList')).get('rights',[])):
            u = self._attr(a, 'rightsURI')
            c = self._text(i)
            if u in self.OA_URIS or c in self.OA_TEXT:
                isoa = True

        # publisher
        pub = r.get('publisher')

        # now populate the 'properties' for this paper
        properties = {}
        if isoa:
            properties['OPEN'] = 1
        if html:
            properties['ELECTR'] = html
        if pdf:
            properties['PDF'] = pdf
        if doi:
            properties['DOI'] = doi

        return { 
            'bibcode': bibcode or '',
            'authors': authors,
            'affiliations': aaffils,
#            'contributors': contributors,
            'title': title,
            'pubdate': pubdate,
            'properties': properties,
            'keywords': keywords,
            'abstract': self.get_abstract(r),
            'references': self.get_references(r),
            'source': pub
            }

    
if __name__ == "__main__":
    
    # allows program to print utf-8 encoded output sensibly
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    dc3 = DataCite3Parser()
    for file in sys.argv[1:]:
        d = None
        with open(file, 'r') as fp:
            d = dc3.parse(fp)
            print json.dumps(d, indent=2)


