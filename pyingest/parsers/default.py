import re
import sys
import bs4 as bs_parser
import xmltodict as xmltodict_parser

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

    def _dehtml(self,r):
        bad_tags = ['p','a','img','hr','font','br','iframe','div','link','html','head','body','title','style','meta','!doctype','span','noscript','button','form','b','li','ul','ol','svg','option','label','text','g','rect','details','summary','strong','header','h1','h2','h3','h4','nav','textarea','include-fragment','details-dialog','time','polygon','footer','path','small','section','circle']
        dx = r.replace('\n',' ').replace('\r',' ')
        for t in bad_tags:
            p1 = '<'+t+' ?.*?>'
            p2 = '</'+t+' ?>'
            d1 = re.sub(p1,' ',dx,flags=re.I)
            dx = re.sub(p2,' ',d1,flags=re.I)
        dx = re.sub('<!--.*?-->',' ',dx,flags=re.I)
        dx = re.sub('<script ?.*?>*?</script>',' ',dx,flags=re.I)
        return re.sub('\s+',' ',dx).strip()
    
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

class BaseBeautifulSoupParser(BaseXmlToDictParser):
    """
    An XML parser which uses BeautifulSoup to create a dictionary
    out of the input XML stream
    """

    def bstodict(self, fp, **kwargs):
        """returns a dict as created by xmltodict"""
        return bs_parser.BeautifulSoup(fp.read(), "xml", **kwargs)
        
