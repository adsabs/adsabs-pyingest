"""
Test parsers
"""
from __future__ import print_function

import unittest
import filecmp
import sys
import os

from pyingest.parsers import pnas

from pyingest.serializers import classic

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'


class TestPnas(unittest.TestCase):

    def setUp(self):
        self.stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')

    # Test 30
    def test_pnas_parser(self):

        webdata_file = os.path.join(self.stubdata_dir, 'input', 'pnas_117_36_21873.xml')
        with open(webdata_file, open_mode_u) as fw:
            webdata = fw.read()
        parser = pnas.PNASParser()
        output = parser.parse(webdata)

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
