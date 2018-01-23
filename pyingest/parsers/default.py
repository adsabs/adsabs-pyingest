import sys
from lib import xmltodict as xmltodict_parser

class MissingParser(Exception):
    pass

class DefaultParser(object):
    """just a stub entry"""
    def __init__(self):
        raise MissingParser("No parser defined")


class BaseXmlToDictParser(object):
    """
    An XML parser which uses xmltodict to create a dictionary
    out of the input XML stream
    """
    
    def xmltodict(self, fp, **kwargs):
        """returns a dict as created by xmltodict"""
        return xmltodict_parser.parse(fp, **kwargs)
        
    def _array(self, e):
        """Ensures that e is an array"""
        if type(e) == type(None):
            return []
        elif type(e) == type([]):
            return e
        else:
            return [e]

    def _dict(self, e, d={}):
        """Ensures that e is a dictionary"""
        if type(e) == type(None):
            return d
        elif isinstance(e, dict):
            return e
        else:
            return d

    def _text(self, e, d=''):
        """Returns text node of element e (or default d)"""
        if type(e) == type(None):
            return d
        elif isinstance(e, dict):
            return e.get('#text', d)
        elif isinstance(e, basestring):
            return e

    def _attr(self, e, k, d=''):
        """Returns attribute k from element e (or default d)"""
        if type(e) == type(None):
            return d
        elif isinstance(e, dict):
            return e.get('@' + k, d)
        elif isinstance(e, basestring):
            return d
        else:
            return d

