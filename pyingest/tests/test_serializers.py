"""
Test serializer
"""

import unittest
import glob
import json
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
from pyingest.parsers.iop import IOPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import *


class TestClassic(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'parsed/*.json'))
        self.outputdir = os.path.join(stubdata_dir, 'serialized')
#        sys.stderr.write("test cases are: {}\n".format(self.inputdocs))

    def test_classic_tagged(self):
        serializer = Tagged()
        for file in self.inputdocs:
            # this will raise exceptions if something is wrong
            document = ''
            with open(file, 'r') as fp:
                document = json.load(fp)
                self.assertIsNotNone(document, "%s: error reading doc" % file)
            outputfp = StringIO()
            serializer.write(document, outputfp)
            output = outputfp.getvalue()
            outputfp.close()
            self.assertNotEqual(output, '')
            basefile, _ = os.path.splitext(os.path.basename(file))
            target = os.path.join(self.outputdir, basefile + '.tag')
            # save temporary copy
            target_saved = target + '.parsed'
            with open(target_saved, 'w') as fp:
                fp.write(output)

            ok = False
            # Python 3 orders the properties dictionary differently
            if sys.version_info > (3,) and os.path.exists(os.path.join(self.outputdir, 'python3', basefile + '.tag')):
                target = os.path.join(self.outputdir, 'python3', basefile + '.tag')
            if os.path.exists(target):
                with open(target, 'r') as fp:
                    shouldbe = fp.read()
                    self.assertEqual(shouldbe, output, "results differ from %s" % target)
                    ok = True
            else:
                sys.stderr.write("could not find shouldbe file %s\n" % target)

            if ok:
                os.remove(target_saved)
            else:
                sys.stderr.write("parsed output saved to %s\n" % target_saved)


class TestReferenceWriter(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata/input')
        self.inputdoc = stubdata_dir + '/iop_apj.xml'
        self.topdir = os.path.join(os.path.dirname(__file__), 'data/output')

    def test_write_refhandler_data(self):
        paperdata = IOPJATSParser()
        with open(self.inputdoc, 'r') as fm:
            pdat = paperdata.parse(fm)
        if 'refhandler_list' in pdat:
            refwriter = ReferenceWriter()
            refwriter.topdir = self.topdir
            refwriter.refsource = '.jats.iopft.xml'
            refwriter.writeref(pdat)
            self.assertEqual('1', '1')
        else:
            self.assertEqual('a', 'b')

    # I changed these to let go with a pass instead of raising an exception
    #
    # def test_no_refdata(self):
    #     refwriter = ReferenceWriter()
    #     with self.assertRaises(NoReferencesException):
    #         refwriter.writeref({})

    # def test_no_metadata(self):
    #     refwriter = ReferenceWriter()
    #     bogus_data = {'refhandler_list': ['fnord']}
    #     with self.assertRaises(WriteErrorException):
    #         refwriter.writeref(bogus_data)
