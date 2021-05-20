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


class TestProQuest(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        config.PROQUEST_BASE_PATH = os.path.join(stubdata_dir, 'input/')
        self.outputdir = os.path.join(stubdata_dir, 'serialized')

    # Test 29
    def test_proquest_parser(self):
        infilename = 'SAO_NASA_Sep_2020.UNX'
        parser = proquest.ProQuestParser(infilename)
        parsed = parser.parse()
        serializer = classic.Tagged()
        standard_outfile = os.path.join(self.outputdir, 'SAO_NASA_Sep_2020.UNX.new')
        test_outfile = os.path.join(self.outputdir, 'test_proquest.UNX.new')
        try:
            os.remove(test_outfile)
        except Exception as err:
            pass
        with open(test_outfile, 'w') as fo:
            for rec in parser.results:
                serializer.write(rec, fo)
        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)
