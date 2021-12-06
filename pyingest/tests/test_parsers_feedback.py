"""
Test parsers
"""
from __future__ import print_function

import unittest
import sys
import os

from pyingest.parsers import adsfeedback

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'


class TestFeedback(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.inputdir = os.path.join(stubdata_dir, 'input/')

    # Test 31
    def test_feedback_parser(self):
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
