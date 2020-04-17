import re
import sys
import bs4
import xmltodict as xmltodict_parser
import urllib
import urllib2
import bs4
import lxml
import warnings
import ssl

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
# The following line is to avoid (when doing JOSS harvesting):
# IOError: [Errno socket error] [SSL: CERTIFICATE_VERIFY_FAILED] certificate
# verify failed (_ssl.c:727)
ssl._create_default_https_context = ssl._create_unverified_context


class MissingParser(Exception):
    pass


class UnknownHarvestMethod(Exception):
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
        if isinstance(e, type(None)):
            return []
        elif isinstance(e, list):
            return e
        else:
            return [e]

    def _dict(self, e, d={}):
        """Ensures that e is a dictionary"""
        if isinstance(e, type(None)):
            return d
        elif isinstance(e, dict):
            return e
        else:
            return d

    def _text(self, e, d=''):
        """Returns text node of element e (or default d)"""
        if isinstance(e, type(None)):
            return d
        elif isinstance(e, dict):
            return e.get('#text', d)
        elif isinstance(e, basestring):
            return e

    def _attr(self, e, k, d=''):
        """Returns attribute k from element e (or default d)"""
        if isinstance(e, type(None)):
            return d
        elif isinstance(e, dict):
            return e.get('@' + k, d)
        elif isinstance(e, basestring):
            return d
        else:
            return d


class BaseBeautifulSoupParser(object):
    """
    An XML parser which uses BeautifulSoup to create a dictionary
    out of the input XML stream.  Used by jats.py and aps.py
    """

    def bsfiletodict(self, fp, **kwargs):
        """returns a BeautifulSoup tree"""
        return bs4.BeautifulSoup(fp.read(), 'html5lib', **kwargs)

    def bsstrtodict(self, r, **kwargs):
        """returns a BeautifulSoup tree"""
        return bs4.BeautifulSoup(r, 'html5lib', **kwargs)


class BaseRSSFeedParser(object):
    """
    A parser that takes an RSS/Atom feed
    """

    control_chars = ''.join(map(unichr, range(0, 32) + range(127, 160)))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))

    def __init__(self):
        self.errors = []
        self.links = []
        pass

    def remove_control_chars(s):
        return control_char_re.sub('', s)

    def get_records(self, rssURL, data_tag='entry', headers={}, **kwargs):
        qparams = urllib.urlencode(kwargs)
        if qparams:
            url = "%s?%s" % (rssURL, qparams)
        else:
            url = rssURL
        if headers:
            req = urllib2.Request(url, headers=headers)
        else:
            req = urllib2.Request(url)
        source = urllib2.urlopen(req)
        soup = bs4.BeautifulSoup(source, 'lxml')
        entries = soup.find_all(data_tag)
        try:
            self.links = soup.find_all('link')
        except Exception, err:
            self.links = []
        return entries

    def parse(self, url, **kwargs):

        rss_recs = [{}]
        data = self.get_records(url, **kwargs)
        for d in data:
            try:
                title = data.find('title').text
            except Exception, err:
                title = ''
            rss_recs.append({
                'title': title,
            })

        return rss_recs
