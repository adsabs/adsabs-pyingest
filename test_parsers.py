"""
Test parsers
"""

import unittest
import sys, os
import glob
import json
import parsers.zenodo
import parsers.arxiv

stubdata_dir = os.path.join(os.path.dirname(__file__), 'test/stubdata')

class TestZenodo(unittest.TestCase):

    def setUp(self):
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'input/zenodo.*'))
        self.outputdir = os.path.join(stubdata_dir, 'parsed')
#        sys.stderr.write("test cases are: {}\n".format(self.inputdocs))

    def test_zenodo_parser(self):
        parser = parsers.zenodo.ZenodoParser()
        for file in self.inputdocs:
            # this will raise exceptions if something is wrong
            with open(file, 'r') as fp:
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

            if ok:
                os.remove(target_saved)
            else:
                sys.stderr.write("parsed output dumped in %s\n" % target_saved)



class TestArxiv(unittest.TestCase):

    def test_bad_xml(self):
        with self.assertRaises(parsers.arxiv.EmptyParserException):
            with open('test/arxiv.test/readme.txt','rU') as fp:
                parser = parsers.arxiv.ArxivParser()
                document = parser.parse(fp)
                print "file parsed ok"

    def test_no_xml_file(self):
        with self.assertRaises(parsers.arxiv.EmptyParserException):
            fp=None
            parser = parsers.arxiv.ArxivParser()
            document = parser.parse(fp)
            print "file parsed ok"

    def test_parsing(self):
        shouldbe = {'authors':'Luger, Rodrigo; Lustig-Yaeger, Jacob; Agol, Eric',
                    'title':'Planet-Planet Occultations in TRAPPIST-1 and Other Exoplanet Systems',
                'url':'http://arxiv.org/abs/1711.05739',
                'doi':None,
                'bibcode':'2017arXiv171105739L'}
        with open('test/arxiv.test/oai_ArXiv.org_1711_05739','rU') as fp:
            parser = parsers.arxiv.ArxivParser()
            document = parser.parse(fp)
        for k in shouldbe.keys():
            self.assertEqual(shouldbe[k],document[k])
        shouldbe['url'] = 'http://www.reddit.com/r/aww'
        self.assertNotEqual(shouldbe['url'],document['url'])

if __name__ == '__main__':
    unittest.main()
