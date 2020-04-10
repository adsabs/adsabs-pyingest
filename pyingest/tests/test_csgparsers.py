"""
Test parsers
"""

import unittest
import filecmp
import sys
import os
import glob
import json

from pyingest.parsers import oup
from pyingest.parsers import iop
from pyingest.config import config
from pyingest.parsers.author_names import AuthorNames

from pyingest.serializers import classic



class TestOUP(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata/')
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'input/oup*'))
        self.outputdir = os.path.join(stubdata_dir, 'parsed')
        sys.stderr.write("test cases are: {}\n".format(self.inputdocs))

    def test_oup_parser(self):
        parser = oup.OUPJATSParser()
        config.REFERENCE_TOPDIR = '/dev/null/'
        for file in self.inputdocs:
            # this will raise exceptions if something is wrong
            with open(file, 'r') as fp:
                test_data = parser.parse(fp)
                self.assertIsNotNone(test_data, "%s: error reading doc" % file)
            basefile = os.path.basename(file)
            target = os.path.join(self.outputdir, basefile + '.json')
            # save temporary copy of data structure
            target_saved = target + '.json'
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

            if ok:
                os.remove(target_saved)
            else:
                sys.stderr.write("parsed output dumped in %s\n" % target_saved)

        return


class TestIOP(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata/')
        self.inputdir = os.path.join(stubdata_dir, 'input')

    def test_iop_parser(self):
        test_infile = os.path.join(self.inputdir, 'iop_apj.xml')
        parser = iop.IOPJATSParser()
        config.REFERENCE_TOPDIR = '/dev/null/'
        with open(test_infile) as fp:
            test_data = parser.parse(fp)
            output_bibcode = '2019ApJ...882...74H'
            output_pub = u'The Astrophysical Journal, Volume 882, Issue 2, id.74'
            output_aff = [u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; Space Sciences Laboratory, 7 Gauss Way, University of California, Berkeley, CA 94720-7450, USA; <id system="ORCID">0000-0002-8548-482X</id>; <email>jhare@berkeley.edu</email>', u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; <id system="ORCID">0000-0002-6447-4251</id>', u'Department of Astronomy & Astrophysics, Pennsylvania State University, 525 Davey Lab, University Park, PA 16802, USA; <id system="ORCID">0000-0002-7481-5259</id>', u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; <id system="ORCID">0000-0001-7833-1043</id>']
            self.assertEqual(test_data['bibcode'], output_bibcode)
            self.assertEqual(test_data['publication'], output_pub)
            self.assertEqual(test_data['affiliations'], output_aff)
        return


