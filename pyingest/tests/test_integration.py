"""
Test parsers
"""

from future import standard_library
standard_library.install_aliases()
from builtins import zip
import unittest
import sys
import os
import glob
import json
import io
from pyingest.parsers import arxiv
from pyingest.serializers import classic


class TestParseAndSerialize(unittest.TestCase):

    def test_arxiv_to_classic(self):
        testfiles = glob.glob(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai*'))
        shouldbe = [f.replace('/oai', '/tagged/oai') + '.tagged' for f in testfiles]
        for f, b in zip(testfiles, shouldbe):
            with open(f, 'rU') as fp:
                serializer = classic.Tagged()
                outputfp = io.StringIO()
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)
                serializer.write(document, outputfp)
                testoutput = outputfp.getvalue()
                outputfp.close()
                with open(b, 'rU') as bp:
                    self.assertEqual(testoutput, bp.read())
