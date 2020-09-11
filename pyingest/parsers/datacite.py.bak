#!/usr/bin/python
#
#

import sys
import json
import codecs
from collections import OrderedDict
from default import BaseXmlToDictParser
from author_names import AuthorNames


class WrongSchemaException(Exception):
    pass


class MissingDoiException(Exception):
    pass


class MissingAuthorsException(Exception):
    pass


class MissingTitleException(Exception):
    pass


class DataCiteParser(BaseXmlToDictParser):
    """DataCiteParser compatible with schema versions 3 and 4"""

    def __init__(self):
        # make sure we are utf-8 clean on stdout, stderr
        self.DC_SCHEMAS = ['http://datacite.org/schema/kernel-3', 'http://datacite.org/schema/kernel-4']
        self.OA_URIS = ['info:eu-repo/semantics/openAccess']
        self.OA_TEXT = ['Open Access']
        self.author_names = AuthorNames()
        self.author_collaborations_params = {
            'keywords': ['group', 'team', 'collaboration'],
            'first_author_delimiter': ':',
            'remove_the': False,
            'fix_arXiv_mixed_collaboration_string': False,
        }

    def get_abstract(self, r):
        # abstract, references are all in the "descriptions" section
        # as of version 3.1 of datacite schema, "References" is not an
        # allowed description type so Lars is shoving the references
        # in a section labeled as "Other" as a json structure
        abstract = None
        for s in self._array(r.get('descriptions', {}).get('description', [])):
            t = s.get('@descriptionType')
            if t == 'Abstract':
                abstract = self._text(s)
        return abstract

    def get_described_by(self, r):
        """
        Record that describes the current record.
            Page 52: https://schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
        """
        relation_type = 'IsDescribedBy'
        return self._get_related_identifiers(r, relation_type)

    def get_description_of(self, r):
        """
        Current record is a description of a given record.
            Page 52: https://schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
        """
        relation_type = 'Describes'
        return self._get_related_identifiers(r, relation_type)

    def get_versions(self, r):
        """
        It relates an unversioned code repository to one of its specific software versions.
            Page 71: https://schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
        """
        relation_type = 'HasVersion'
        return self._get_related_identifiers(r, relation_type)

    def get_version_of(self, r):
        """
        It relates a specific version of a software package to its software code repository.
            Page 71: https://schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
        """
        relation_type = 'IsVersionOf'
        return self._get_related_identifiers(r, relation_type)

    def get_forked_from(self, r):
        """
        It denotes software that is a fork of other software
            Page 71: https://schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
        """
        relation_type = 'IsDerivedFrom'
        return self._get_related_identifiers(r, relation_type)

    def get_forks(self, r):
        """
        It denotes software that is the origin of a fork
            Page 71: https://schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
        """
        relation_type = 'IsSourceOf'
        return self._get_related_identifiers(r, relation_type)

    def get_citations(self, r):
        relation_type = 'IsCitedBy'
        return self._get_related_identifiers(r, relation_type)

    def get_references(self, r):
        relation_type = 'Cites'
        return self._get_related_identifiers(r, relation_type)

    def _get_related_identifiers(self, r, relation_type):
        related_identifiers = []
        for s in self._array(self._dict(r.get('relatedIdentifiers')).get('relatedIdentifier', [])):
            t = s.get('@relationType')
            c = self._text(s)
            if t == relation_type:
                related_identifiers.append(c)
        return related_identifiers

    def get_doctype(self, r):
        """
        Resource type
            Page 43: https://schema.datacite.org/meta/kernel-4.1/doc/DataCite-MetadataKernel_v4.1.pdf
        """
        datacite_resourcetype_mapping = {
            'Audiovisual': 'misc',
            'Collection': 'misc',
            'DataPaper': 'misc',
            'Dataset': 'misc',
            'Event': 'misc',
            'Image': 'misc',
            'InteractiveResource': 'misc',
            'Model': 'misc',
            'PhysicalObject': 'misc',
            'Service': 'misc',
            'Software': 'software',
            'Sound': 'misc',
            'Text': 'misc',
            'Workflow': 'misc',
            'Other': 'misc',
        }
        return datacite_resourcetype_mapping.get(r.get('resourceType', {}).get('@resourceTypeGeneral', None), "misc")

    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
        # as a convenience, remove the OAI wrapper if it's there
        r = d.get('record', {}).get('metadata', {}).get('resource') or d.get('resource')
        return r

    def parse(self, fp, **kwargs):
        """
        DataCite 3.1 metadata returns ADS tagged format.
        Note: we use the object's _dict() and _array() functions to guard against
        unexpeected element constructs in the XML (e.g. empty elements or single
        sub-elements when a list is allowed
        """
        r = self.resource_dict(fp, **kwargs)

        # check for namespace to make sure it's a compatible datacite schema
        schema = r.get('@xmlns')
        if schema not in self.DC_SCHEMAS:
            raise WrongSchemaException("Unexpected XML schema \"%s\"" % schema)

        if 'DOI' != r.get('identifier', {}).get('@identifierType', ''):
            raise MissingDoiException("//identifier['@identifierType'] not DOI!")
        doi = r.get('identifier').get('#text')

        # authors
        authors = []
        normalized_authors = []
        aaffils = []
        for a in self._array(self._dict(r.get('creators')).get('creator', [])):
            creator_name = a.get('creatorName')
            if type(creator_name) is OrderedDict:
                creator_name = creator_name.get("#text")
            creator_name = self.author_names.parse(creator_name, collaborations_params=self.author_collaborations_params)
            normalized_creator_name = self.author_names._normalize(creator_name, collaborations_params=self.author_collaborations_params)
            authors.append(creator_name)
            normalized_authors.append(normalized_creator_name)
            aff = a.get('affiliation', '')
            if aff is None:
                aff = ''
            for i in self._array(a.get('nameIdentifier')):
                if 'ORCID' == i.get('@nameIdentifierScheme') or \
                        'http://orcid.org' == i.get('@schemeURI'):
                    aff = aff + ' <ORCID>' + i.get('#text') + '</ORCID>'
            aaffils.append(aff.strip())
        if not authors:
            raise MissingAuthorsException("No authors found for")

        # title
        titles = {}
        for t in self._array(self._dict(r.get('titles')).get('title', [])):
            title_attr = self._attr(t, 'lang', 'en')
            titles[title_attr] = self._text(t)
        if not titles:
            raise MissingTitleException("No title found")
        # we use the english title as the main one
        # then add any foreign ones
        title = titles.pop('en')
        for tkey in titles:
            title += ' <TITLE lang="%s">%s</TITLE>' % (tkey, titles[tkey])

        # publication year and date
        year = self._text(r.get('publicationYear'))
        pubdate = None
        dates = {}
        for d in self._array(self._dict(r.get('dates')).get('date', [])):
            t = self._attr(d, 'dateType')
            dates[t] = self._text(d)
        for dt in ['Issued', 'Created', 'Submitted']:
            if dt in dates:
                pubdate = dates[dt]
        if not pubdate:
            pubdate = year

        # keywords
        keywords = []
        for k in self._array(self._dict(r.get('subjects')).get('subject', [])):
            # XXX we are ignoring keyword scheme
            keywords.append(self._text(k))

        # contributors (non-authors)
        contribs = []
        caffils = []
        ctypes = []
        for a in self._array(self._dict(r.get('contributors')).get('contributor', [])):
            contribs.append(a.get('contributorName'))
            ctypes.append(a.get('@contributorType', ''))
            aff = a.get('affiliation', '')
            if aff is None:
                aff = ''
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
        for i in self._array(self._dict(r.get('alternateIdentifiers')).get('alternateIdentifier', [])):
            t = i.get('@alternateIdentifierType')
            if t == 'URL':
                html = self._text(i)
            elif t == 'bibcode':
                bibcode = self._text(i)
            else:
                identifiers[t] = self._text(i)

        # related identifiers; bibcodes sometime appear in <relatedIdentifiers>
        for i in self._array(self._dict(r.get('relatedIdentifiers')).get('relatedIdentifier', [])):
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
        for i in self._array(self._dict(r.get('rightsList')).get('rights', [])):
            u = self._attr(i, 'rightsURI')
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

        version = r.get('version', "")

        return {
            'bibcode': bibcode or '',
            'authors': authors,
            'normalized_authors': normalized_authors,
            'affiliations': aaffils,
            # 'contributors': contributors,
            'title': title,
            'pubdate': pubdate,
            'properties': properties,
            'keywords': keywords,
            'abstract': self.get_abstract(r),
            'references': self.get_references(r),
            'citations': self.get_citations(r),
            'doctype': self.get_doctype(r),
            'version': version,
            'versions': self.get_versions(r),
            'version_of': self.get_version_of(r),
            'forked_from': self.get_forked_from(r),
            'forks': self.get_forks(r),
            'described_by': self.get_described_by(r),
            'description_of': self.get_description_of(r),
            'source': pub}

#
#
# if __name__ == "__main__":
#
#    # allows program to print utf-8 encoded output sensibly
#    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
#    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
#
#    dc = DataCiteParser()
#    for file in sys.argv[1:]:
#        d = None
#        with open(file, 'r') as fp:
#            d = dc.parse(fp)
#            print json.dumps(d, indent=2)
