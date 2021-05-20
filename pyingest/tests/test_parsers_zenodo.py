"""
Test parsers
"""
from __future__ import print_function

import unittest
import filecmp
import sys
import os
import glob
import json
import shutil
from mock import patch, Mock, mock_open

from pyingest.parsers import zenodo
from pyingest.config import config
from pyingest.parsers.author_names import AuthorNames
from pyingest.parsers.affils import AffiliationParser
from pyingest.parsers import adsfeedback

from pyingest.serializers import classic

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'


class TestZenodo(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'input/zenodo*'))
        self.outputdir = os.path.join(stubdata_dir, 'parsed')
        sys.stderr.write("test cases are: {}\n".format(self.inputdocs))

    # Test 1
    def test_zenodo_parser(self):
        parser = zenodo.ZenodoParser()
        for file in self.inputdocs:
            # this will raise exceptions if something is wrong
            with open(file, open_mode) as fp:
                document = parser.parse(fp)
                self.assertIsNotNone(document, "%s: error reading doc" % file)
            basefile = os.path.basename(file)
            target = os.path.join(self.outputdir, basefile + '.json')
            # save temporary copy of data structure
            target_saved = target + '.parsed'
            with open(target_saved, 'w') as fp:
                json.dump(document, fp, sort_keys=True, indent=4)

            ok = False
            if os.path.exists(target):
                with open(target, 'r') as fp:
                    shouldbe = json.load(fp)
                    self.assertDictEqual(shouldbe, document, "results differ from %s" % target)
                    ok = True
            else:
                sys.stderr.write("could not find shouldbe file %s\n" % target)

            os.remove(target_saved)
