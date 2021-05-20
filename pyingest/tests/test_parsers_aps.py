"""
Test parsers
"""
from __future__ import print_function

import unittest
import filecmp
import sys
import os
import glob
import json
import shutil
from mock import patch, Mock, mock_open

from pyingest.parsers import aps
from pyingest.parsers import arxiv
from pyingest.parsers import atel
from pyingest.parsers import datacite
from pyingest.parsers import gcncirc
from pyingest.parsers import hstprop
from pyingest.parsers import iop
from pyingest.parsers import joss
from pyingest.parsers import oup
from pyingest.parsers import pnas
from pyingest.parsers import proquest
from pyingest.parsers import procsci
from pyingest.parsers import zenodo
from pyingest.config import config
from pyingest.parsers.author_names import AuthorNames
from pyingest.parsers.affils import AffiliationParser
from pyingest.parsers import adsfeedback

from pyingest.serializers import classic

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'

class MockResponse(object):

    def __init__(self, resp_data):
        self.resp_data = resp_data

    def read(self):
        return self.resp_data


class TestAPSJATS(unittest.TestCase):

    # Test 17
    def test_unicode_initial(self):
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevB.96.081117.fulltext.xml')
        shouldbe = {'bibcode': '2017PhRvB..96h1117S'}
        with open(testfile, open_mode_u) as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
        self.assertEqual(document['bibcode'], shouldbe['bibcode'])

    # Test 18
    def test_dehtml(self):
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevA.97.019999.fulltext.xml')
        shouldbe = {'title': 'Finite-error metrological bounds on multiparameter Hamiltonian estimation'}
        with open(testfile, open_mode_u) as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
        self.assertEqual(document['title'], shouldbe['title'])

    # Test 19
    def test_dehtml2(self):
        self.maxDiff = None
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevA.95.129999.fulltext.xml')
        shouldbe = {'bibcode': u'2015PhRvA..95l9999T', 'publication': u'Physical Review A, Volume 95, Issue 1, id.129999, <NUMPAGES>9</NUMPAGES> pp.', 'pubdate': u'07/2015', 'copyright': u'&#169;2018 American Physical Society', 'title': u'Fake article title with other kinds of markup inside <a href="http://www.reddit.com/r/aww">it</a> including paragraph tags that really have no place in a title.', 'abstract': u'<a href="http://naughtywebsite.gov">Fake URLs</a> are an increasing problem when trying to write fake abstracts. It\'s unlikely that a .gov domain would host a bad website, but then again what times are we living in now? Also, <inline-formula><mml:math><mml:mi>&#948;</mml:mi></mml:math></inline-formula>. Also also, <inline-formula><mml:math>this is some math</mml:math></inline-formula>.', 'database': ['PHY'], 'page': u'129999', 'volume': u'95', 'affiliations': [u'NASA-ADS, Harvard-Smithsonian Center for Astrophysics, 60 Garden St., Cambridge, MA 02138, United States', u'Monty Python lol.'], 'authors': u'Templeton, Matthew; Organs, Harry Snapper', 'keywords': u'Fundamental concepts', 'issue': u'1', 'properties': {'DOI': u'10.1103/PhysRevA.95.129999'}, 'refhandler_list': ['<ref id="c1"><label>[1]</label><mixed-citation publication-type="journal"><object-id>1</object-id><person-group person-group-type="author"><string-name>A. S. Holevo</string-name></person-group>, <source/>J. Multivariate Anal. <volume>3</volume>, <page-range>337</page-range> (<year>1973</year>).<pub-id pub-id-type="coden">JMVAAI</pub-id><issn>0047-259X</issn><pub-id assigning-authority="crossref" pub-id-type="doi" specific-use="suppress-display">10.1016/0047-259X(73)90028-6</pub-id></mixed-citation></ref>']}
        with open(testfile, open_mode_u) as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
        self.assertDictEqual(document, shouldbe)
