"""
Test parsers
"""
from __future__ import print_function

import unittest
import filecmp
import sys
import os
from mock import patch

from pyingest.parsers import proquest
from pyingest.serializers import classic

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'


class TestProQuest(unittest.TestCase):

    def setUp(self):
        self.stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata/')
        # config.PROQUEST_BASE_PATH = os.path.join(stubdata_dir, 'input/')
        self.outputdir = os.path.join(self.stubdata_dir, 'serialized')

    # Test 29
    def test_proquest_parser(self):
        marc_filename = self.stubdata_dir + 'input/' + 'SAO_NASA_Sep_2020.UNX'
        oa_filename = marc_filename.replace('.UNX', '_OpenAccessTitles.csv')
        marcdata = open(marc_filename).read()
        oadata = open(oa_filename).read()
        parser = proquest.ProQuestParser(marcdata,oadata)
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
