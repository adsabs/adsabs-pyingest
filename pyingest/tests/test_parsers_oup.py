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

from pyingest.parsers import aps
from pyingest.parsers import arxiv
from pyingest.parsers import atel
from pyingest.parsers import datacite
from pyingest.parsers import gcncirc
from pyingest.parsers import hstprop
from pyingest.parsers import iop
from pyingest.parsers import joss
from pyingest.parsers import oup
from pyingest.parsers import pnas
from pyingest.parsers import proquest
from pyingest.parsers import procsci
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

class MockResponse(object):

    def __init__(self, resp_data):
        self.resp_data = resp_data

    def read(self):
        return self.resp_data


class TestOUP(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata/')
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'input/oup*'))
        self.maxDiff = None
        self.outputdir = os.path.join(stubdata_dir, 'parsed')
        self.tmplogdir = os.path.join(os.path.dirname(__file__), 'data/oup_tempfiles/')
        # sys.stderr.write("test cases are: {}\n".format(self.inputdocs))
        self.FAKE_OUP_TMP_DIRS = {
            'mnrasl': self.tmplogdir + 'MNRASL',
            'mnras':  self.tmplogdir + 'MNRAS',
            'pasj.':  self.tmplogdir + 'PASJ',
            'geoji':  self.tmplogdir + 'GeoJI'
        }

    # Test 16
    def test_oup_parser(self):
        with patch.dict(config.OUP_TMP_DIRS, self.FAKE_OUP_TMP_DIRS, clear=True):
            parser = oup.OUPJATSParser()
            for file in self.inputdocs:
                # this will raise exceptions if something is wrong
                with open(file, open_mode_u) as fp:
                    input_data = fp.read()
                test_data = parser.parse(input_data)
                self.assertIsNotNone(test_data, "%s: error reading doc" % file)
                basefile = os.path.basename(file)
           
                target = os.path.join(self.outputdir, basefile + '.parsed')

                # post-parsing cleanup:
                for f in glob.glob(self.tmplogdir + 'backup/*'):
                    fi = os.path.basename(f)
                    fo = self.tmplogdir + fi
                    try:
                        shutil.copyfile(f, fo)
                    except Exception as err:
                        pass

                # # save temporary copy of data structure
                # target_saved = target + '.NEW'
                # with open(target_saved, 'w') as fp:
                    # json.dump(test_data, fp, sort_keys=True, indent=4)

                with open(target, 'r') as fp:
                    shouldbe = json.load(fp)
                    self.assertDictEqual(shouldbe, test_data, "results differ from %s" % target)

                
        return
