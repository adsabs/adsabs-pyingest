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
from mock import patch, Mock

from pyingest.parsers import procsci

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


class TestProcSci(unittest.TestCase):

    def setUp(self):
        # Mock procsci.PoSParser.urllib.urlopen
        self.patcher = patch('requests.get')
        self.requests_mock = self.patcher.start()

    # Test 20
    def test_output(self):
        parser = procsci.PoSParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/pos_sissa_it_299.html")
        mock_data = open(mock_infile, open_mode_u).read()
        self.requests_mock.return_value.text = MockResponse(mock_data)
        test_data = parser.parse("https://pos.sissa.it/299_test")
        test_outfile = "test_pos.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/procsci_299.tag")
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

    # Test 21
    def test_badsite(self):
        parser = procsci.PoSParser()
        with self.assertRaises(procsci.URLError):
            test_data = parser.parse("https://www.cnn.com")

    def tearDown(self):
        self.patcher.stop()
