"""
Test parsers
"""
from __future__ import print_function

import unittest
import filecmp
import os
import json
from mock import patch

from pyingest.parsers import hstprop
from pyingest.serializers import classic


class TestHSTProp(unittest.TestCase):

    def setUp(self):
        # Mock hstprop.HSTParser.get_batch
        self.patcher = patch('pyingest.parsers.hstprop.HSTParser.get_batch')
        self.get_batch_mock = self.patcher.start()

    # Test 22
    def test_output(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop.json")
        mock_data = json.loads(open(mock_infile).read())
        self.get_batch_mock.return_value = mock_data
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query_test'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1, test=True)
        test_outfile = "test_hst.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/hstprop.tag")
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

    # Test 23
    def test_missing_token(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop.json")
        mock_data = json.loads(open(mock_infile).read())
        self.get_batch_mock.return_value = mock_data
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query_test'
        with self.assertRaises(hstprop.RequestError):
            test_data = parser.parse(api_url, fromDate='2019-01-01', maxRecords=1, test=True)

    # Test 24
    def test_missing_field(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop_missing_field.json")
        mock_data = json.loads(open(mock_infile).read())
        self.get_batch_mock.return_value = mock_data
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query_test'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1, test=True)
        # A missing data error should be reported
        self.assertEqual(parser.errors[0], 'Found record with missing data: HST Proposal#15677')

    # Test 25
    def test_misaligned_arrays(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop_misaligned_arrays.json")
        mock_data = json.loads(open(mock_infile).read())
        self.get_batch_mock.return_value = mock_data
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query_test'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1, test=True)
        # Misaligned arrays should be reported
        self.assertEqual(parser.errors[0], 'Found misaligned affiliation/ORCID arrays: 2019hst..prop15677M')

    def tearDown(self):
        self.patcher.stop()
