#!/usr/bin/python
#
#

import sys
import json
import re
import logging
from datacite3 import DataCite3Parser


class WrongPublisherException(Exception):
    pass

class ZenodoParser(DataCite3Parser):

    def get_references(self, r):
        # as of version 3.1 of datacite schema, "References" is not an
        # allowed description type so Lars is shoving the references
        # in a section labeled as "Other" as a json structure
        references = []
        for s in self._array(r.get('descriptions',{}).get('description',[])):
            t = s.get('@descriptionType')
            c = self._text(s)
            if t == 'References':
                # XXX not supported yet, but one can only hope...
                references = c.split('\n')
            elif t == 'Other':
                try:
                    j = json.loads(c)
                    references = j.get('references',[])
                except ValueError:
                    logging.warning(u'Ignoring unparsable "Other" description element: %s\n' % c)
        return references

    def get_abstract(self, r):
        abs = super(ZenodoParser, self).get_abstract(r)
        abs = re.sub(r'\s*<p>', '', abs)
        abs = re.sub(r'</p>\s*$', '', abs)
        return abs

    def parse(self, fp, **kwargs):
        """Parses Zenodo's flavor of DataCite 3.1 schema, returns ADS tagged format"""

        doc = super(self.__class__, self).parse(fp, **kwargs)
        # r = self._resource
        return doc

        # publisher
        pub = doc.get('source')
        if pub != 'Zenodo' and pub != 'ZENODO':
            raise WrongPublisherException("Found publisher field of \"%s\" rather than Zenodo" % pub)
        else:
            doc['source'] = 'ZENODO'

        return doc

    
if __name__ == "__main__":
    
    # allows program to print utf-8 encoded output sensibly
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    parser = ZenodoParser()
    for file in sys.argv[1:]:
        d = None
        with open(file, 'r') as fp:
            d = parser.parse(fp)
            print json.dumps(d, indent=2)


