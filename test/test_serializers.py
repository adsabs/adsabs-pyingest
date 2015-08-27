"""
Test serializer
"""

import unittest
import sys, os
import glob
import json
import cStringIO
import serializers.classic

stubdata_dir = os.path.join(os.path.dirname(__file__), 'stubdata')

class TestClassic(unittest.TestCase):

    def setUp(self):
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'parsed/*.json'))
        self.outputdir = os.path.join(stubdata_dir, 'serialized')
#        sys.stderr.write("test cases are: {}\n".format(self.inputdocs))

    def test_classic_tagged(self):
        serializer = serializers.classic.Tagged()
        for file in self.inputdocs:
            # this will raise exceptions if something is wrong
            document = ''
            with open(file, 'r') as fp:
                document = json.load(fp)
                self.assertIsNotNone(document, "%s: error reading doc" % file)
            outputfp = cStringIO.StringIO()
            serializer.write(document, outputfp)
            output = outputfp.getvalue()
            outputfp.close()
            self.assertNotEqual(output, '')
            basefile, _ = os.path.splitext(os.path.basename(file))
            target = os.path.join(self.outputdir, basefile + '.tag')
            # check to see if a file exists
            ok = False
            if os.path.exists(target):
                with open(target, 'r') as fp:
                    shouldbe = fp.read()
                    self.assertEqual(shouldbe, output, "results differ from %s" % target)
            else:
                self.fail("could not find shouldbe file %s\n" % target)
            if not ok:
                # dump copy of data structure
                target = target + '.parsed'
                with open(target, 'w') as fp:
                    fp.write(output)
#                    sys.stderr.write("created file %s\n" % target)


