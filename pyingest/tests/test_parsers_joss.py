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


class TestJOSS(unittest.TestCase):

    def setUp(self):
        # Mock joss.JOSSParser.urllib.urlopen
        if sys.version_info > (3,):
            self.patcher = patch('urllib.request.urlopen')
        else:
            self.patcher = patch('urllib2.urlopen')
        self.urlopen_mock = self.patcher.start()

    # Test 26
    def test_output(self):
        parser = joss.JOSSParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/joss_atom.xml")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        joss_url = 'https://joss.theoj.org/papers/published.atom.test'
        test_data = parser.parse(joss_url, since='2019-07-10', page=1)
        test_outfile = "test_joss.tag"
        if sys.version_info > (3,):
            standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/python3/joss.tag")
        else:
            standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/joss.tag")
        try:
            os.remove(test_outfile)
        except Exception as err:
            pass
        for d in test_data:
            serializer = classic.Tagged()
            outputfp = open(test_outfile, 'a')
            serializer.write(d, outputfp)
            outputfp.close()
        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)

    def tearDown(self):
        self.patcher.stop()
