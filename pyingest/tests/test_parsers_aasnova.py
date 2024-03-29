"""
Test parsers
"""
from __future__ import print_function

import unittest
import filecmp
import sys
import os
from mock import patch, Mock

from pyingest.parsers import aasnova

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


class TestAASNova(unittest.TestCase):

    def setUp(self):
        # Mock aasnova.AASNovaParser.urllib.urlopen
        if sys.version_info > (3,):
            self.patcher = patch('urllib.request.urlopen')
        else:
            self.patcher = patch('urllib2.urlopen')
        self.urlopen_mock = self.patcher.start()

    # Test 27
    def test_output(self):
        parser = aasnova.AASNovaParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/AASNova_rss.xml")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        aasnova_url = 'https://aasnova.org/?feed=rss2'
        test_data = parser.parse(aasnova_url, data_tag='item')
        test_outfile = "test_aasnova.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/aasnova.tag")
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
