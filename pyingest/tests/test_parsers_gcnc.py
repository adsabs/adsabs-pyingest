"""
Test parsers
"""
from __future__ import print_function

import unittest
import os

from pyingest.parsers import gcncirc


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
