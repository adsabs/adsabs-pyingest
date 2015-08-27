"""
Test parsers
"""

import unittest
import sys, os
import glob
import json
import validators.ads

stubdata_dir = os.path.join(os.path.dirname(__file__), 'stubdata')

class TestSimple(unittest.TestCase):

    def setUp(self):
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'parsed/*.json'))
#        sys.stderr.write("test cases are: {}\n".format(self.inputdocs))

    def test_simple_schema(self):
        validator = validators.ads.SimpleValidator()
        for file in self.inputdocs:
            # this will raise exceptions if something is wrong
            with open(file, 'r') as fp:
                document = json.load(fp)
                self.assertIsNotNone(document, "%s: error reading doc" % file)
            validator.validate(document)


