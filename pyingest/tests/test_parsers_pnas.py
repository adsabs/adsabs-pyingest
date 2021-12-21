"""
Test parsers
"""
from __future__ import print_function

import unittest
import filecmp
import sys
import os
import json
from mock import patch, Mock, mock_open

from pyingest.parsers import pnas

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


class TestPnas(unittest.TestCase):

    def setUp(self):
        self.stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.patcher = patch('requests.get')
        self.requests_mock = self.patcher.start()

    # Test 30
    def test_pnas_parser(self):
        mock_infile = os.path.join(self.stubdata_dir, 'input', 'pnas_feedparser.resp')
        mock_html_file = os.path.join(self.stubdata_dir, 'input', 'pnas_resp.html')
        mock_data = open(mock_infile, open_mode_u).read()
        mock_html = open(mock_html_file, open_mode_u).read()
        self.requests_mock.return_value.text = MockResponse(mock_html)
        feed = json.loads(mock_data)
        for _item in feed['entries']:
            absURL = _item['link']
            parser = pnas.PNASParser()
            output = parser.parse(absURL)

        serializer = classic.Tagged()
        test_outfile = os.path.join(self.stubdata_dir, 'serialized', 'test_pnas.tag')
        if sys.version_info > (3,):
            standard_outfile = os.path.join(self.stubdata_dir, 'serialized', 'python3', 'pnas.tag')
        else:
            standard_outfile = os.path.join(self.stubdata_dir, 'serialized', 'pnas.tag')
        try:
            os.remove(test_outfile)
        except Exception as err:
            pass
        with open(test_outfile, 'w') as fo:
            serializer.write(output, fo)

        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)
