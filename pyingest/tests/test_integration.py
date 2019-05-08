"""
Test parsers
"""

import unittest
import sys, os
import glob
import json
import cStringIO
from pyingest.parsers import arxiv
from pyingest.serializers import classic

class TestParseAndSerialize(unittest.TestCase):

    def test_arxiv_to_classic(self):
        testfiles = glob.glob('test_data/arxiv.test/oai*')
        shouldbe = [f.replace('/oai','/tagged/oai') + '.tagged' for f in testfiles]
        for f,b in zip(testfiles,shouldbe):
            with open(f,'rU') as fp:
                serializer = classic.Tagged()
                outputfp = cStringIO.StringIO()
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)
                serializer.write(document, outputfp)
                testoutput = outputfp.getvalue()
                outputfp.close()
                with open (b,'rU') as bp:
                    self.assertEqual(testoutput,bp.read())
