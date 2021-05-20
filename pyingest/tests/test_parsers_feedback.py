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


class TestFeedback(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.inputdir = os.path.join(stubdata_dir, 'input/')

    # Test 31
    def test_gcn_parser(self):
        test_infile = os.path.join(self.inputdir, 'ads_feedback.json')
        with open(test_infile) as fp:
            data = fp.read()
            parser = adsfeedback.ADSFeedbackParser(data)
            test_data = parser.parse()
            output_bibcode = '2525ApJ..9999.9999T'
            output_affil = ['Center for Astrophysics | Harvard & Smithsonian <id system="ORCID">0000-0003-1918-0622</id>']
            # print(test_data['affiliations'])
            self.assertEqual(test_data['bibcode'], output_bibcode)
            self.assertEqual(test_data['affiliations'], output_affil)
