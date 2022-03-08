"""
Test parsers
"""

import unittest
import sys
import os
import json

from pyingest.parsers import jats

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'

class TestJATS(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata/')
        self.inputdir = os.path.join(stubdata_dir, 'input')
        self.maxDiff = None

    # Populate keywords if only UAT terms are given
    def test_uat_keyword_population(self):
        test_infile = os.path.join(self.inputdir, 'apj_uat_keys_test.xml')
        parser = jats.JATSParser()
        with open(test_infile, open_mode_u) as fp:
            input_data = fp.read()
        test_data = parser.parse(input_data)

        test_uat_string = test_data['uatkeys']
        test_uat_list = test_uat_string.strip().split(', ')
        test_uat_list.sort()

        test_keys_string = test_data['keywords']
        test_keys_list = test_keys_string.strip().split(', ')
        test_keys_list.sort()

        expected_uat_list = ['1964','1483','1989','1485','2009','1974','1477','1503','1476','1533','1493','2170']
        expected_uat_list.sort()

        expected_keys_list = ['Magnetohydrodynamics', 'Solar corona', 'Solar coronal heating', 'Solar coronal loops', 'Radiative magnetohydrodynamics', 'Solar active regions', 'Solar atmosphere', 'Solar magnetic fields', 'Solar physics', 'Solar ultraviolet emission', 'Solar extreme ultraviolet emission', 'Extreme ultraviolet astronomy']
        expected_keys_list.sort()

        self.assertEqual(test_uat_list, expected_uat_list)
        self.assertEqual(test_keys_list, expected_keys_list)
        return
