"""
Test parsers
"""

import unittest
import sys
import os
import glob

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
from pyingest.parsers import arxiv
from pyingest.serializers import classic


class TestParseAndSerialize(unittest.TestCase):

    def test_arxiv_to_classic(self):
        testfiles = glob.glob(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai*'))
        shouldbe = [f.replace('/oai', '/tagged/oai') + '.tagged' for f in testfiles]
        for f, b in zip(testfiles, shouldbe):
            # Python 3 orders the properties dictionary differently
            if sys.version_info > (3,) and os.path.exists(b.replace('/tagged/oai', '/tagged/python3/oai')):
                b = b.replace('/tagged/oai', '/tagged/python3/oai')
            if sys.version_info > (3,):
                open_mode = 'rb'
            else:
                open_mode = 'rU'
            with open(f, open_mode) as fp:
                serializer = classic.Tagged()
                outputfp = StringIO()
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)
                serializer.write(document, outputfp)
                testoutput = outputfp.getvalue()
                outputfp.close()
                if sys.version_info > (3,):
                    read_mode = 'r'
                else:
                    read_mode = 'rU'
                with open(b, read_mode) as bp:
                    self.assertEqual(testoutput, bp.read())
