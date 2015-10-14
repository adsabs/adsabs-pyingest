#!/usr/bin/python
#
#

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

class TeiXmlParser(BaseXmlToDictParser):

    def __init__(self):
        # make sure we are utf-8 clean on stdout, stderr
        self.TEI_SCHEMA = 'http://www.tei-c.org/ns/1.0'
        self.debug = False

    def get_abstract(self, header):
        """
        abstract is found inside the section element "teiHeader/profileDesc/abstract"
        """
        abstract = [ p for p in self._array(header.get('profileDesc',{}).get('abstract',{}).get('p',[])) ]
        return "\n".join(abstract) if abstract else None

    def get_references(self, text):
        """
        references are found in "text/back/div/listBibl"
        """
        references = []
        for div in self._array(text.get('back',{}).get('div',[])):
            t = div.get('@type','')
            if t != 'references':
                continue
            for bib in self._array(div.get('listBibl',{}).get('biblStruct',[])):
                title = self._text(bib.get('analytic',{}).get('title'))
                authors = ", ".join([self.parse_author(a) for a in self._array(bib.get('analytic',{}).get('author',[]))])
                monodict = self.parse_monograph(bib.get('monogr',{}))
                # now normalize this down to a string that our reference resolver does well with
                refstring = ''
                refstring += authors or monodict.get('authors') or monodict.get('editors')
                refstring += " " + monodict.get('pubdate', '')
                refstring += " " + (monodict.get('journal') or monodict['title'] or title)
                refstring += " " + monodict.get('volume', '')
                refstring += " " + monodict.get('page', '')
                refstring = refstring.strip()
                references.append(refstring)
        return references

    def parse_monograph(self, monogr):
        """
        here we deal with:
        - parsing of journal names "<title level="j">ApJ</title>"
        - parsing of book names "<title level="m">ASP Conf. Ser</title>"
        - parsing of editors "<editor>M. Mehringer, R. L. Plante, &amp; D. A. Roberts</editor>"
        - parsing of book authors: (structure described in parse_author() below)
        - parsing of imprint information (volume, issue, page, pubdate, pubpage, publisher):
                <imprint>
                        <biblScope unit="volume">35</biblScope>
                        <biblScope unit="page">29</biblScope>
                        <date type="published" when="1992" />
                </imprint>
        """
        if not monogr:
            return {}

        if self.debug:
            sys.stderr.write("parsing monograph: {0}\n".format(monogr))
        editors = self._text(monogr.get('editor'))
        bookauthors = [self.parse_author(a) for a in self._array(monogr.get('author',[]))]

        # make dictionary out of all possible <title> combinations
        titledict = dict([(self._attr(t, 'level'), self._text(t)) 
                          for t in self._array(monogr.get('title',{}))])
        journal = titledict.get('j')
        booktitle = titledict.get('m')
        # biblscopes contains volume, page, etc
        # this works for cases where we have <imprint/>
        imprint = monogr.get('imprint') or {} 
        for s in self._array(imprint.get('biblScope',[])):
            if self.debug:
                sys.stderr.write("biblScope array: {0}\n".format(s))
        bibscopes = dict([(self._attr(s, 'unit'), self._text(s))
                          for s in self._array(imprint.get('biblScope',[]))])
        # pubdates and the like
        pubdates = dict([(self._attr(d, 'type'), self._attr(d, 'when')) 
                         for d in self._array(imprint.get('date',[]))])
        pubdate = pubdates.get('published') or pubdates.get('online')
        
        monodict = bibscopes
        if bookauthors: monodict['authors'] = ", ".join(bookauthors)
        if editors: monodict['editors'] = editors
        if booktitle: monodict['title'] = booktitle
        if journal: monodict['journal'] = journal
        if pubdate: monodict['pubdate'] = pubdate
        
        return monodict
            
     
    def parse_author(self, author):
        """
        parses a TEI author structure into a string
        example TEI XML is:
                <author>
                        <persName>
                                <forename type="first">C</forename>
                                <forename type="middle">S</forename>
                                <surname>Grant</surname>
                        </persName>
                </author>
        which is already parsed in the following input data structure:
            {u'persName': {u'forename': {u'@type': u'first'}, {'#text': u'C'}}, 
                          {u'forename': {u'@type': u'middle'}, {'#text': u'S'}}, 
                          {u'surname': u'Grant'}}
        """
        first_, middle, last_ = '', '', ''
        if self.debug:
            sys.stderr.write("parsing author: {0}\n".format(author))
        last_ = self._text(author.get('persName',{}).get('surname')).strip()
        for n in self._array(author.get('persName',{}).get('forename',[])):
            t = self._attr(n, 'type')
            if t == 'first':
                first_ = self._text(n).strip()
            elif t == 'middle':
                middle = self._text(n).strip()
            else:
                logging.debug("ignoring element type '%s' in persName" % t)

        if first_ and len(first_) == 1: first_ += '.'
        if middle and len(middle) == 1: middle += '.'
        a = (last_ + ', ' + first_ + ' ' + middle).strip()
        return a
                                 
     
    def parse_affiliation(self, author):
        """
        parses a TEI author structure into a string
        example TEI XML is:
                <author>
                        <persName>
                                <forename type="first">C</forename>
                                <forename type="middle">S</forename>
                                <surname>Grant</surname>
                        </persName>
                </author>
        which is already parsed in the following input data structure:
            {u'persName': {u'forename': {u'@type': u'first'}, {'#text': u'C'}}, 
                          {u'forename': {u'@type': u'middle'}, {'#text': u'S'}}, 
                          {u'surname': u'Grant'}}
        """
        org, address = '', ''
        org = self._text(author.get('affiliation',{}).get('orgName')).strip()
        ainfo = author.get('affiliation',{}).get('address',{})
        affil = [ org ]
        for k in ('settlement', 'region', 'postCode'):
            if (ainfo.get(k)): affil.append(ainfo[k]) 

        return ", ".join(affil)
                                 

    def resource_dict(self, fp, **kwargs):
        d = self.xmltodict(fp, **kwargs)
        r = d.get('TEI',{})
        return r

    def parse(self, fp, debug=False, **kwargs):
        """
        parses TEI XML generated by Grobid
        """
        if debug:
            self.debug = True

        r = self.resource_dict(fp, **kwargs)

        # check for namespace to make sure it's the TEI flavor we understand
        schema = r.get('@xmlns')
        if schema != self.TEI_SCHEMA:
            raise WrongSchemaException("Unexpected XML schema \"%s\"" % schema)

        header = r.get('teiHeader',{})
        if not header:
            raise MissingHeaderException("TEI header not found")
        text = r.get('text',{})
        if not text:
            raise MissingTextException("TEI text not found")

        # authors
        authors = []
        aaffils = []
        for a in self._array(header.get('fileDesc',{}).get('sourceDesc',{}).get('biblStruct',{}).get('analytic',{}).get('author',[])):
            authors.append(self.parse_author(a))
            aaffils.append(self.parse_affiliation(a))
        if not authors:
            raise MissingAuthorsException("No authors found for")

        # title
        titles = []
        for t in self._array(header.get('fileDesc',{}).get('titleStmt',{}).get('title',[])):
            titles.append(self._text(t))
        if not titles:
            raise MissingTitleException("No title found")

        # should we use just top title?
        title = ". ".join(titles)

        # publication year and date
        pubdate = None
        dates = {}
        for d in self._array(header.get('fileDesc',{}).get('publicationStmt',{}).get('date',[])):
            t = self._attr(d, 'type')
            dates[t] = self._attr(d, 'when')
        for dt in [ 'created', 'submitted', 'published' ]:
            if dt in dates:
                pubdate = dates[dt]

        abstract = self.get_abstract(header)
        references = self.get_references(text)

        res = {}
        if authors: res['authors'] = authors
        if aaffils: res['affiliations'] = aaffils
        if title: res['title'] = title
        if pubdate: res['pubdate'] = pubdate
        if abstract: res['abstract'] = abstract
        if references: res['references'] = references
        return res

    
if __name__ == "__main__":
    
    # allows program to print utf-8 encoded output sensibly
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    p = TeiXmlParser()
    for file in sys.argv[1:]:
        d = None
        with open(file, 'r') as fp:
            d = p.parse(fp)
            print json.dumps(d, indent=2)


