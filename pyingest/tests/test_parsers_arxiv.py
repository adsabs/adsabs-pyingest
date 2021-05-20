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

from pyingest.parsers import arxiv
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


class TestArxiv(unittest.TestCase):

    # Test 11
    def test_bad_xml(self):
        with self.assertRaises(arxiv.EmptyParserException):
            with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/readme.txt'), open_mode_u) as fp:
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)

    # Test 12
    def test_parsing(self):
        shouldbe = {'authors': u'Luger, Rodrigo; Lustig-Yaeger, Jacob; Agol, Eric',
                    'title': u'Planet-Planet Occultations in TRAPPIST-1 and Other Exoplanet Systems',
                    'bibcode': u'2017arXiv171105739L'}
        with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_1711_05739'), open_mode_u) as fp:
            parser = arxiv.ArxivParser()
            document = parser.parse(fp)
        for k in shouldbe.keys():
            self.assertEqual(shouldbe[k], document[k])
        shouldbe['title'] = 'Paper that has nothing to do with TRAPPIST-1'
        self.assertNotEqual(shouldbe['title'], document['title'])

    # Test 13
    def test_unicode_init(self):
        shouldbe = {'bibcode': u'2009arXiv0901.2443O'}
        with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_0901_2443'), open_mode_u) as fp:
            parser = arxiv.ArxivParser()
            document = parser.parse(fp)
            self.assertEqual(document['bibcode'], shouldbe['bibcode'])

    # Test 14
    def test_old_style_subjects(self):
        testfiles = [os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_astro-ph_9501013'),
                     os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_math_0306266'),
                     os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_hep-th_0408048'),
                     os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_cond-mat_9706061')]
        shouldbe = [{'bibcode': u'1995astro.ph..1013H'}, {'bibcode': u'2003math......6266C'}, {'bibcode': u'2004hep.th....8048S'}, {'bibcode': u'1997cond.mat..6061A'}]
        for f, b in zip(testfiles, shouldbe):
            with open(f, open_mode_u) as fp:
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)
                self.assertEqual(document['bibcode'], b['bibcode'])
