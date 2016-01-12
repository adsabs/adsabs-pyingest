import sys
import string
import itertools
import logging
from dateutil.parser import parse as dateparser
from collections import OrderedDict
from namedentities import numeric_entities, named_entities


# some utility functions
letters = [ c for c in string.uppercase ]
double_aff = [ "%c%c" % (x,y) for (x,y) in itertools.product(letters,letters) ]
triple_aff = [ "%s%c" % (x,y) for (x,y) in itertools.product(double_aff,letters) ]
AFFILIATION_LABELS = double_aff + triple_aff

def format_affids(affils):
    """
    Formats an array of affiliations using the ADS Classic syntax:
    [ 'AA(blabla)', 'AB(foobar)', ... ]
    """
    formatted = []
    for i in range(len(affils)):
        f = u"{0}({1})".format(AFFILIATION_LABELS[i], affils[i])
        formatted.append(f)
    return formatted

def format_pubdate(date):
    parsed = dateparser(date)
    return parsed.strftime("%Y/%m")

class Tagged(object):
    
    fieldDict = OrderedDict([('bibcode',      { 'tag': 'R' }),
                             ('title',        { 'tag': 'T' }),
                             ('authors',      { 'tag': 'A', 'join': '; ' }),
                             ('affiliations', { 'tag': 'F', 'join': ', ', 'fmt': format_affids }),
                             ('pubdate',      { 'tag': 'D', 'fmt': format_pubdate }),
                             ('publication',  { 'tag': 'J' }),
                             ('source',       { 'tag': 'G'  }),
                             ('keywords',     { 'tag': 'K', 'join': ', ' }),
                             ('abstract',     { 'tag': 'B' }),
                             ('properties',   { 'tag': 'I', 'join': '; ' }),
                             ('references',   { 'tag': 'Z', 'join': "\n   " }),
                             ])

    @classmethod
    def write(cls, record, fp=sys.stdout):
        for field in cls.fieldDict:
            content = record.get(field)
            if field is 'bibcode' and content is None:
                continue
            elif not content:
                continue
            d = cls.fieldDict.get(field)
            fmt = d.get('fmt')
            if fmt:
                content = fmt(content)
            jc = d.get('join','')
            if type(content) is type([]):
                content = jc.join(content)
            elif type(content) is type({}):
                content = jc.join([u"{0}: {1}".format(k, v) for k,v in content.items()])
            try:
                fp.write('%{0} {1}\n'.format(d.get('tag'), named_entities(content)))
            except:
                logging.error("error writing content for tag {0}: {1}\n".format(d.get('tag'), named_entities(content)))
                raise
        fp.write('\n')



