"""
Test parsers
"""

import unittest
import filecmp
import sys
import os
import glob
import json
from mock import patch, Mock

from pyingest.parsers import datacite
from pyingest.parsers import zenodo
from pyingest.parsers import arxiv
from pyingest.parsers import aps
from pyingest.parsers import procsci
from pyingest.parsers import hstprop
from pyingest.parsers import joss
from pyingest.parsers import atel
from pyingest.parsers.author_names import AuthorNames

from pyingest.serializers import classic


class TestDatacite(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'input/datacite-example-*'))
        self.outputdir = os.path.join(stubdata_dir, 'parsed')
        sys.stderr.write("test cases are: {}\n".format(self.inputdocs))

    def test_datacite_parser(self):
        parser = datacite.DataCiteParser()
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


class TestZenodo(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.inputdocs = glob.glob(os.path.join(stubdata_dir, 'input/zenodo*'))
        self.outputdir = os.path.join(stubdata_dir, 'parsed')
        sys.stderr.write("test cases are: {}\n".format(self.inputdocs))

    def test_zenodo_parser(self):
        parser = zenodo.ZenodoParser()
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


class TestAuthorNames(unittest.TestCase):

    def setUp(self):
        self.author_names = AuthorNames()

    def test_default_author_names(self):
        authors_str = u"robert white smith; m. power; maria antonia de la paz; bla., bli.; the collaboration: john stuart; collaboration, Gaia; John; github_handle;;.."
        expected_authors_str = u"white smith, robert; power, m.; de la paz, maria antonia; bla., bli.; the collaboration; stuart, john; collaboration, Gaia; John; github_handle; Unknown, Unknown; .."
        # Default
        corrected_authors_str = self.author_names.parse(authors_str)
        self.assertEqual(corrected_authors_str, expected_authors_str)

    def test_normalize_author_names(self):
        authors_str = u"robert white smith; m. power; maria antonia de la paz; bla., bli.; the collaboration: john stuart; collaboration, Gaia; John; github_handle;;.."
        corrected_authors_str = u"white smith, robert; power, m; de la paz, maria antonia; bla, bli; the collaboration; stuart, john; collaboration, Gaia; John; github_handle; Unknown, Unknown; Unknown, Unknown"
        expected_normalized_authors_str = u"White Smith, R; Power, M; De La Paz, M A; Bla, B; the collaboration; Stuart, J; collaboration Gaia; John; github_handle; Unknown, U; Unknown, U"
        # Normalize
        normalized_authors_str = self.author_names.normalize(corrected_authors_str)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)
        normalized_authors_str = self.author_names.parse(authors_str, normalize=True)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_ignore_collaborations_in_author_names(self):
        authors_str = u"robert white smith; m. power; maria antonia de la paz; bla., bli.; the collaboration: john stuart; collaboration, Gaia; John; github_handle;;.."
        expected_normalized_authors_str = "White Smith, R; Power, M; De La Paz, M A; Bla, B; Stuart, T C J; Collaboration, G; John; github_handle; Unknown, U; Unknown, U"
        collaborations_params = {
            'keywords': [],
            'first_author_delimiter': None,
            'remove_the': False,
            'fix_arXiv_mixed_collaboration_string': False,
        }
        normalized_authors_str = self.author_names.parse(authors_str, normalize=True, collaborations_params=collaborations_params)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_remove_the_from_collaborations_in_author_names(self):
        authors_str = u"robert white smith; m. power; maria antonia de la paz; bla., bli.; the collaboration: john stuart; collaboration, Gaia; John; github_handle;;.."
        expected_normalized_authors_str = u"White Smith, R; Power, M; De La Paz, M A; Bla, B; collaboration; Stuart, J; collaboration Gaia; John; github_handle; Unknown, U; Unknown, U"
        collaborations_params = {
            'keywords': ['group', 'team', 'collaboration'],
            'first_author_delimiter': ':',
            'remove_the': True,
            'fix_arXiv_mixed_collaboration_string': False,
        }
        normalized_authors_str = self.author_names.parse(authors_str, normalize=True, collaborations_params=collaborations_params)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_ignore_names_in_collaborations_in_author_names(self):
        authors_str = u"robert white smith; m. power; maria antonia de la paz; bla., bli.; the collaboration: john stuart; collaboration, Gaia; John; github_handle;;.."
        expected_normalized_authors_str = u"White Smith, R; Power, M; De La Paz, M A; Bla, B; the collaboration: john stuart; collaboration Gaia; John; github_handle; Unknown, U; Unknown, U"
        collaborations_params = {
            'keywords': ['group', 'team', 'collaboration'],
            'first_author_delimiter': None,
            'remove_the': False,
            'fix_arXiv_mixed_collaboration_string': False,
        }
        normalized_authors_str = self.author_names.parse(authors_str, normalize=True, collaborations_params=collaborations_params)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_fix_arXiv_mixed_collaboration_string(self):
        authors_str = u"robert white smith; m. power; maria antonia de la paz; bla., bli.; the collaboration: john stuart; collaboration, Gaia; John; github_handle;;.."
        expected_normalized_authors_str = u"White Smith, R; Power, M; De La Paz, M A; Bla, B; the collaboration: john stuart; Gaia collaboration; John; github_handle; Unknown, U; Unknown, U"
        collaborations_params = {
            'keywords': ['group', 'team', 'collaboration'],
            'first_author_delimiter': None,
            'remove_the': False,
            'fix_arXiv_mixed_collaboration_string': True,
        }
        normalized_authors_str = self.author_names.parse(authors_str, normalize=True, collaborations_params=collaborations_params)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)


class TestArxiv(unittest.TestCase):

    def test_bad_xml(self):
        with self.assertRaises(arxiv.EmptyParserException):
            with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/readme.txt'), 'rU') as fp:
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)

    def test_parsing(self):
        shouldbe = {'authors': u'Luger, Rodrigo; Lustig-Yaeger, Jacob; Agol, Eric',
                    'title': u'Planet-Planet Occultations in TRAPPIST-1 and Other Exoplanet Systems',
                    'bibcode': u'2017arXiv171105739L'}
        with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_1711_05739'), 'rU') as fp:
            parser = arxiv.ArxivParser()
            document = parser.parse(fp)
        for k in shouldbe.keys():
            self.assertEqual(shouldbe[k], document[k])
        shouldbe['title'] = 'Paper that has nothing to do with TRAPPIST-1'
        self.assertNotEqual(shouldbe['title'], document['title'])

    def test_unicode_init(self):
        shouldbe = {'bibcode': u'2009arXiv0901.2443O'}
        with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_0901_2443'), 'rU') as fp:
            parser = arxiv.ArxivParser()
            document = parser.parse(fp)
            self.assertEqual(document['bibcode'], shouldbe['bibcode'])

    def test_old_style_subjects(self):
        testfiles = [os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_astro-ph_9501013'),
                     os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_math_0306266'),
                     os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_hep-th_0408048'),
                     os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_cond-mat_9706061')]
        shouldbe = [{'bibcode': u'1995astro.ph..1013H'}, {'bibcode': u'2003math......6266C'}, {'bibcode': u'2004hep.th....8048S'}, {'bibcode': u'1997cond.mat..6061A'}]
        for f, b in zip(testfiles, shouldbe):
            with open(f, 'rU') as fp:
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)
                self.assertEqual(document['bibcode'], b['bibcode'])


class TestAPSJATS(unittest.TestCase):

    def test_unicode_initial(self):
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevB.96.081117.fulltext.xml')
        shouldbe = {'bibcode': '2017PhRvB..96h1117S'}
        with open(testfile, 'rU') as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
        self.assertEqual(document['bibcode'], shouldbe['bibcode'])

    def test_dehtml(self):
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevA.97.019999.fulltext.xml')
        shouldbe = {'title': 'Finite-error metrological bounds on multiparameter Hamiltonian estimation'}
        with open(testfile, 'rU') as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
        self.assertEqual(document['title'], shouldbe['title'])

    def test_dehtml2(self):
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevA.95.129999.fulltext.xml')
        shouldbe = {'bibcode': u'2015PhRvA..95l9999T', 'publication': u'Physical Review A, Volume 95, Issue 1, id.129999', 'pubdate': u'07/2015', 'copyright': u'\xa92018 American Physical Society', 'title': u'Fake article title with other kinds of markup inside <a href="http://www.reddit.com/r/aww">it</a> including paragraph tags that really have no place in a title.', 'abstract': u'<a href="http://naughtywebsite.gov">Fake URLs</a> are an increasing problem when trying to write fake abstracts. It\'s unlikely that a .gov domain would host a bad website, but then again what times are we living in now? Also, <inline-formula><mml:math><mml:mi>\u03b4</mml:mi></mml:math></inline-formula>. Also also, <inline-formula><mml:math>this is some math</mml:math></inline-formula>.', 'database': ['PHY'], 'page': u'129999', 'volume': u'95', 'affiliations': [u'NASA-ADS, Harvard-Smithsonian Center for Astrophysics, 60 Garden St., Cambridge, MA 02138, United States', u'Monty Python lol.'], 'authors': u'Templeton, Matthew; Organs, Harry Snapper', 'keywords': u'Fundamental concepts', 'issue': u'1', 'properties': {'DOI': u'10.1103/PhysRevA.95.129999'}}
        with open(testfile, 'rU') as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
        self.assertDictEqual(document, shouldbe)


class MockResponse(object):

    def __init__(self, resp_data):
        self.resp_data = resp_data

    def read(self):
        return self.resp_data


class TestProcSci(unittest.TestCase):

    def setUp(self):
        "Mock procsci.PoSParser.urllib.urlopen"
        self.patcher = patch('urllib.urlopen')
        self.urlopen_mock = self.patcher.start()

    def test_output(self):
        parser = procsci.PoSParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/pos_sissa_it_299.html")
        mock_data = open(mock_infile, 'rU').read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        test_data = parser.parse("https://pos.sissa.it/299")
        test_outfile = "test_pos.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/procsci_299.tag")
        try:
            os.remove(test_outfile)
        except Exception, err:
            pass
        for d in test_data:
            serializer = classic.Tagged()
            outputfp = open(test_outfile, 'a')
            serializer.write(d, outputfp)
            outputfp.close()
        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)

    def test_badsite(self):
        parser = procsci.PoSParser()
        with self.assertRaises(procsci.URLError):
            test_data = parser.parse("https://www.cnn.com")

    def tearDown(self):
        self.patcher.stop()


class TestHSTProp(unittest.TestCase):
    import pytest

    def setUp(self):
        "Mock hstprop.HSTParser.urllib.urlopen"
        self.patcher = patch('urllib2.urlopen')
        self.urlopen_mock = self.patcher.start()

    def test_output(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop.json")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1, test=True)
        test_outfile = "test_hst.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/hstprop.tag")
        try:
            os.remove(test_outfile)
        except Exception, err:
            pass
        for d in test_data:
            serializer = classic.Tagged()
            outputfp = open(test_outfile, 'a')
            serializer.write(d, outputfp)
            outputfp.close()
        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)

    def test_missing_token(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop.json")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query'
        with self.assertRaises(hstprop.RequestError):
            test_data = parser.parse(api_url, fromDate='2019-01-01', maxRecords=1)

    def test_missing_field(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop_missing_field.json")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1)
        # A missing data error should be reported
        self.assertEqual(parser.errors[0], 'Found record with missing data: HST Proposal#15677')

    def test_misaligned_arrays(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop_misaligned_arrays.json")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1)
        # Misaligned arrays should be reported
        self.assertEqual(parser.errors[0], 'Found misaligned affiliation/ORCID arrays: 2019hst..prop15677M')

    def tearDown(self):
        self.patcher.stop()


class TestJOSS(unittest.TestCase):
    import pytest

    def setUp(self):
        "Mock joss.JOSSParser.urllib.urlopen"
        self.patcher = patch('urllib2.urlopen')
        self.urlopen_mock = self.patcher.start()

    def test_output(self):
        parser = joss.JOSSParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/joss_atom.xml")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        joss_url = 'https://joss.theoj.org/papers/published.atom'
        test_data = parser.parse(joss_url, since='2019-07-10', page=1)
        test_outfile = "test_joss.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/joss.tag")
        try:
            os.remove(test_outfile)
        except Exception, err:
            pass
        for d in test_data:
            serializer = classic.Tagged()
            outputfp = open(test_outfile, 'a')
            serializer.write(d, outputfp)
            outputfp.close()
        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)

    def tearDown(self):
        self.patcher.stop()

class TestATel(unittest.TestCase):
    import pytest

    def setUp(self):
        "Mock atel.ATelParser.urllib.urlopen"
        self.patcher = patch('urllib2.urlopen')
        self.urlopen_mock = self.patcher.start()

    def test_output(self):
        parser = atel.ATelParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/ATel_rss.xml")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        joss_url = 'http://www.astronomerstelegram.org/?adsbiblio'
        test_data = parser.parse(joss_url, data_tag='item')
        test_outfile = "test_atel.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/atel.tag")
        try:
            os.remove(test_outfile)
        except Exception, err:
            pass
        for d in test_data:
            serializer = classic.Tagged()
            outputfp = open(test_outfile, 'a')
            serializer.write(d, outputfp)
            outputfp.close()
        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)

    def tearDown(self):
        self.patcher.stop()