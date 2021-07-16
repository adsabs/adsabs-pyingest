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

from pyingest.parsers import gcncirc
from pyingest.parsers.author_names import AuthorNames
from pyingest.parsers.affils import AffiliationParser

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


class TestGCNC(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.inputdir = os.path.join(stubdata_dir, 'input/gcncirc')

    # Test 28
    def test_gcn_parser(self):
        test_infile = os.path.join(self.inputdir, '25321.gcn3')
        with open(test_infile) as fp:
            data = fp.read()
            parser = gcncirc.GCNCParser(data)
            test_data = parser.parse()
            output_bibcode = '2019GCN.25321....1I'
            output_authors = 'IceCube Collaboration'
            output_pub = u'GRB Coordinates Network, Circular Service, No. 25321'
            self.assertEqual(test_data['bibcode'], output_bibcode)
            self.assertEqual(test_data['authors'], output_authors)
            self.assertEqual(test_data['publication'], output_pub)
