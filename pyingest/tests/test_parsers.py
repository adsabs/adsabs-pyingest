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

from pyingest.serializers import classic

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'

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

            # if ok:
            #     os.remove(target_saved)
            # else:
            #     sys.stderr.write("parsed output dumped in %s\n" % target_saved)
            os.remove(target_saved)


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

            # if ok:
            #     os.remove(target_saved)
            # else:
            #     sys.stderr.write("parsed output dumped in %s\n" % target_saved)
            os.remove(target_saved)


class TestAuthorNames(unittest.TestCase):

    def setUp(self):
        self.author_names = AuthorNames()
        self.authors_str = u"robert white smith; m. power; maria antonia de la paz; bla., bli.; the collaboration: john stuart; collaboration, gaia; john; github_handle;;.."

    def test_default_author_names(self):
        # expected_authors_str = u"white smith, robert; power, m.; de la paz, maria antonia; bla., bli.; Collaboration; stuart, john; Collaboration, Gaia; John; github_handle; Unknown, Unknown; .."
        expected_authors_str = u"white smith, robert; power, m.; de la paz, maria antonia; bla., bli.; Collaboration; stuart, john; Collaboration, gaia; john; github_handle; ; .."
        # Default
        corrected_authors_str = self.author_names.parse(self.authors_str)
        self.assertEqual(corrected_authors_str, expected_authors_str)

    def test_normalize_author_names(self):
        corrected_authors_str = u"white smith, Robert; power, M; de la paz, Maria Antonia; bla, Bli; Collaboration; stuart, John; Collaboration, gaia; john; github_handle; ; "
        expected_normalized_authors_str = u"white smith, R; power, M; de la paz, M A; bla, B; Collaboration; stuart, J; Collaboration gaia; john; github_handle; ; "
        # Normalize
        normalized_authors_str = self.author_names._normalize(corrected_authors_str)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)
        normalized_authors_str = self.author_names.parse(self.authors_str, normalize=True)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_ignore_collaborations_in_author_names(self):
        expected_normalized_authors_str = "white smith, R; power, M; de la paz, M A; bla, B; stuart, T C J; collaboration, G; john; github_handle; ; "
        collaborations_params = {
            'keywords': [],
            'first_author_delimiter': None,
            'remove_the': False,
            'fix_arXiv_mixed_collaboration_string': False,
        }
        normalized_authors_str = self.author_names.parse(self.authors_str, normalize=True, collaborations_params=collaborations_params)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_remove_the_from_collaborations_in_author_names(self):
        expected_normalized_authors_str = u"white smith, R; power, M; de la paz, M A; bla, B; Collaboration; stuart, J; Collaboration gaia; john; github_handle; ; "
        collaborations_params = {
            'keywords': ['group', 'team', 'collaboration'],
            'first_author_delimiter': ':',
            'remove_the': True,
            'fix_arXiv_mixed_collaboration_string': False,
        }
        normalized_authors_str = self.author_names.parse(self.authors_str, normalize=True, collaborations_params=collaborations_params)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_ignore_names_in_collaborations_in_author_names(self):
        expected_normalized_authors_str = u"white smith, R; power, M; de la paz, M A; bla, B; the Collaboration: john stuart; Collaboration gaia; john; github_handle; ; "
        collaborations_params = {
            'keywords': ['group', 'team', 'collaboration'],
            'first_author_delimiter': None,
            'remove_the': False,
            'fix_arXiv_mixed_collaboration_string': False,
        }
        normalized_authors_str = self.author_names.parse(self.authors_str, normalize=True, collaborations_params=collaborations_params)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_fix_arXiv_mixed_collaboration_string(self):
        expected_normalized_authors_str = u"white smith, R; power, M; de la paz, M A; bla, B; the Collaboration: john stuart; gaia Collaboration; john; github_handle; ; "
        collaborations_params = {
            'keywords': ['group', 'team', 'collaboration'],
            'first_author_delimiter': None,
            'remove_the': False,
            'fix_arXiv_mixed_collaboration_string': True,
        }
        normalized_authors_str = self.author_names.parse(self.authors_str, normalize=True, collaborations_params=collaborations_params)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    def test_dutch_people(self):
        input_names = u"Berg, Imme van den; Imme van den Berg; 't Hooft, Gerard; Hooft, Gerard 't; Hooft, Bas van't; van't Hooft, Bas"
        expected_output_names = u"van den Berg, I; van den Berg, I; 't Hooft, G; 't Hooft, G; van't Hooft, B; van't Hooft, B"
        output_names = self.author_names.parse(input_names, normalize=True)
        self.assertEqual(output_names, expected_output_names)


class TestArxiv(unittest.TestCase):

    def test_bad_xml(self):
        with self.assertRaises(arxiv.EmptyParserException):
            with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/readme.txt'), open_mode_u) as fp:
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)

    def test_parsing(self):
        shouldbe = {'authors': u'Luger, Rodrigo; Lustig-Yaeger, Jacob; Agol, Eric',
                    'title': u'Planet-Planet Occultations in TRAPPIST-1 and Other Exoplanet Systems',
                    'bibcode': u'2017arXiv171105739L'}
        with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_1711_05739'), open_mode_u) as fp:
            parser = arxiv.ArxivParser()
            document = parser.parse(fp)
        for k in shouldbe.keys():
            self.assertEqual(shouldbe[k], document[k])
        shouldbe['title'] = 'Paper that has nothing to do with TRAPPIST-1'
        self.assertNotEqual(shouldbe['title'], document['title'])

    def test_unicode_init(self):
        shouldbe = {'bibcode': u'2009arXiv0901.2443O'}
        with open(os.path.join(os.path.dirname(__file__), 'data/arxiv.test/oai_ArXiv.org_0901_2443'), open_mode_u) as fp:
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
            with open(f, open_mode_u) as fp:
                parser = arxiv.ArxivParser()
                document = parser.parse(fp)
                self.assertEqual(document['bibcode'], b['bibcode'])


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
            output_pub = u'The Astrophysical Journal, Volume 882, Issue 2, id.74, <NUMPAGES>13</NUMPAGES> pp.'
            output_aff = [u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; Space Sciences Laboratory, 7 Gauss Way, University of California, Berkeley, CA 94720-7450, USA; <id system="ORCID">0000-0002-8548-482X</id>; <email>jhare@berkeley.edu</email>', u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; <id system="ORCID">0000-0002-6447-4251</id>', u'Department of Astronomy & Astrophysics, Pennsylvania State University, 525 Davey Lab, University Park, PA 16802, USA; <id system="ORCID">0000-0002-7481-5259</id>', u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; <id system="ORCID">0000-0001-7833-1043</id>']
            self.assertEqual(test_data['bibcode'], output_bibcode)
            self.assertEqual(test_data['publication'], output_pub)
            self.assertEqual(test_data['affiliations'], output_aff)
        return


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
            with open(file, open_mode_u) as fp:
                test_data = parser.parse(fp)
                self.assertIsNotNone(test_data, "%s: error reading doc" % file)
            basefile = os.path.basename(file)
            target = os.path.join(self.outputdir, basefile + '.json')
            # save temporary copy of data structure
            target_saved = target + '.json'
            with open(target_saved, 'w') as fp:
                json.dump(test_data, fp, sort_keys=True, indent=4)

            ok = False
            if os.path.exists(target):
                with open(target, 'r') as fp:
                    shouldbe = json.load(fp)
                    self.assertDictEqual(shouldbe, test_data, "results differ from %s" % target)
                    ok = True
            else:
                sys.stderr.write("could not find shouldbe file %s\n" % target)

            # if ok:
            #     os.remove(target_saved)
            # else:
            #     sys.stderr.write("parsed output dumped in %s\n" % target_saved)
            os.remove(target_saved)

        return


class TestAPSJATS(unittest.TestCase):

    def test_unicode_initial(self):
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevB.96.081117.fulltext.xml')
        shouldbe = {'bibcode': '2017PhRvB..96h1117S'}
        with open(testfile, open_mode_u) as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
        self.assertEqual(document['bibcode'], shouldbe['bibcode'])

    def test_dehtml(self):
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevA.97.019999.fulltext.xml')
        shouldbe = {'title': 'Finite-error metrological bounds on multiparameter Hamiltonian estimation'}
        with open(testfile, open_mode_u) as fp:
            parser = aps.APSJATSParser()
            document = parser.parse(fp)
        self.assertEqual(document['title'], shouldbe['title'])

    def test_dehtml2(self):
        self.maxDiff = None
        testfile = os.path.join(os.path.dirname(__file__), 'data/stubdata/input/apsjats_10.1103.PhysRevA.95.129999.fulltext.xml')
        shouldbe = {'bibcode': u'2015PhRvA..95l9999T', 'publication': u'Physical Review A, Volume 95, Issue 1, id.129999, <NUMPAGES>9</NUMPAGES> pp.', 'pubdate': u'07/2015', 'copyright': u'\xa92018 American Physical Society', 'title': u'Fake article title with other kinds of markup inside <a href="http://www.reddit.com/r/aww">it</a> including paragraph tags that really have no place in a title.', 'abstract': u'<a href="http://naughtywebsite.gov">Fake URLs</a> are an increasing problem when trying to write fake abstracts. It\'s unlikely that a .gov domain would host a bad website, but then again what times are we living in now? Also, <inline-formula><mml:math><mml:mi>\u03b4</mml:mi></mml:math></inline-formula>. Also also, <inline-formula><mml:math>this is some math</mml:math></inline-formula>.', 'database': ['PHY'], 'page': u'129999', 'volume': u'95', 'affiliations': [u'NASA-ADS, Harvard-Smithsonian Center for Astrophysics, 60 Garden St., Cambridge, MA 02138, United States', u'Monty Python lol.'], 'authors': u'Templeton, Matthew; Organs, Harry Snapper', 'keywords': u'Fundamental concepts', 'issue': u'1', 'properties': {'DOI': u'10.1103/PhysRevA.95.129999'}, 'refhandler_list': ['<ref id="c1"><label>[1]</label><mixed-citation publication-type="journal"><object-id>1</object-id><person-group person-group-type="author"><string-name>A. S. Holevo</string-name></person-group>, <source/>J. Multivariate Anal. <volume>3</volume>, <page-range>337</page-range> (<year>1973</year>).<pub-id pub-id-type="coden">JMVAAI</pub-id><issn>0047-259X</issn><pub-id assigning-authority="crossref" pub-id-type="doi" specific-use="suppress-display">10.1016/0047-259X(73)90028-6</pub-id></mixed-citation></ref>']}
        with open(testfile, open_mode_u) as fp:
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
        # Mock procsci.PoSParser.urllib.urlopen
        self.patcher = patch('requests.get')
        self.requests_mock = self.patcher.start()

    def test_output(self):
        parser = procsci.PoSParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/pos_sissa_it_299.html")
        mock_data = open(mock_infile, open_mode_u).read()
        self.requests_mock.return_value.text = MockResponse(mock_data)
        test_data = parser.parse("https://pos.sissa.it/299_test")
        test_outfile = "test_pos.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/procsci_299.tag")
        try:
            os.remove(test_outfile)
        except Exception as err:
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

    def setUp(self):
        # Mock hstprop.HSTParser.get_batch
        self.patcher = patch('pyingest.parsers.hstprop.HSTParser.get_batch')
        self.get_batch_mock = self.patcher.start()

    def test_output(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop.json")
        mock_data = json.loads(open(mock_infile).read())
        # self.get_batch_mock.return_value = MockResponse(mock_data)
        self.get_batch_mock.return_value = mock_data
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query_test'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1, test=True)
        test_outfile = "test_hst.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/hstprop.tag")
        try:
            os.remove(test_outfile)
        except Exception as err:
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
        mock_data = json.loads(open(mock_infile).read())
        # self.get_batch_mock.return_value = MockResponse(mock_data)
        self.get_batch_mock.return_value = mock_data
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query_test'
        with self.assertRaises(hstprop.RequestError):
            test_data = parser.parse(api_url, fromDate='2019-01-01', maxRecords=1, test=True)

    def test_missing_field(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop_missing_field.json")
        mock_data = json.loads(open(mock_infile).read())
        # self.get_batch_mock.return_value = MockResponse(mock_data)
        self.get_batch_mock.return_value = mock_data
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query_test'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1, test=True)
        # A missing data error should be reported
        self.assertEqual(parser.errors[0], 'Found record with missing data: HST Proposal#15677')

    def test_misaligned_arrays(self):
        parser = hstprop.HSTParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/hstprop_misaligned_arrays.json")
        mock_data = json.loads(open(mock_infile).read())
        self.get_batch_mock.return_value = mock_data
        api_url = 'https://proper.stsci.edu/proper/adsProposalSearch/query_test'
        token = 'foo'
        test_data = parser.parse(api_url, api_key=token, fromDate='2019-01-01', maxRecords=1, test=True)
        # Misaligned arrays should be reported
        self.assertEqual(parser.errors[0], 'Found misaligned affiliation/ORCID arrays: 2019hst..prop15677M')

    def tearDown(self):
        self.patcher.stop()


class TestJOSS(unittest.TestCase):

    def setUp(self):
        # Mock joss.JOSSParser.urllib.urlopen
        if sys.version_info > (3,):
            self.patcher = patch('urllib.request.urlopen')
        else:
            self.patcher = patch('urllib2.urlopen')
        self.urlopen_mock = self.patcher.start()

    def test_output(self):
        parser = joss.JOSSParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/joss_atom.xml")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        joss_url = 'https://joss.theoj.org/papers/published.atom.test'
        test_data = parser.parse(joss_url, since='2019-07-10', page=1)
        test_outfile = "test_joss.tag"
        if sys.version_info > (3,):
            standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/python3/joss.tag")
        else:
            standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/joss.tag")
        try:
            os.remove(test_outfile)
        except Exception as err:
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

    def setUp(self):
        # Mock atel.ATelParser.urllib.urlopen
        if sys.version_info > (3,):
            self.patcher = patch('urllib.request.urlopen')
        else:
            self.patcher = patch('urllib2.urlopen')
        self.urlopen_mock = self.patcher.start()

    def test_output(self):
        parser = atel.ATelParser()
        mock_infile = os.path.join(os.path.dirname(__file__), "data/stubdata/input/ATel_rss.xml")
        mock_data = open(mock_infile).read()
        self.urlopen_mock.return_value = MockResponse(mock_data)
        joss_url = 'http://www.astronomerstelegram.org/?adsbiblio.test'
        test_data = parser.parse(joss_url, data_tag='item')
        test_outfile = "test_atel.tag"
        standard_outfile = os.path.join(os.path.dirname(__file__), "data/stubdata/serialized/atel.tag")
        try:
            os.remove(test_outfile)
        except Exception as err:
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


class TestGCNC(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.inputdir = os.path.join(stubdata_dir, 'input/gcncirc')

    def test_gcn_parser(self):
        test_infile = os.path.join(self.inputdir, '25321.gcn3')
        with open(test_infile) as fp:
            data = fp.read()
            parser = gcncirc.GCNCParser(data)
            test_data = parser.parse()
            output_bibcode = '2019GCN.25321....1I'
            output_authors = 'IceCube Collaboration'
            output_pub = u'GRB Coordinates Network, Circular Service, No. 25321'
            self.assertEqual(test_data['bibcode'], output_bibcode)
            self.assertEqual(test_data['authors'], output_authors)
            self.assertEqual(test_data['publication'], output_pub)


class TestProQuest(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        config.PROQUEST_BASE_PATH = os.path.join(stubdata_dir, 'input/')
        self.outputdir = os.path.join(stubdata_dir, 'serialized')

    def test_proquest_parser(self):
        infilename = 'SAO_NASA_Sep_2020.UNX'
        parser = proquest.ProQuestParser(infilename)
        parsed = parser.parse()
        serializer = classic.Tagged()
        standard_outfile = os.path.join(self.outputdir, 'SAO_NASA_Sep_2020.UNX.new')
        test_outfile = os.path.join(self.outputdir, 'test_proquest.UNX.new')
        try:
            os.remove(test_outfile)
        except Exception as err:
            pass
        with open(test_outfile, 'w') as fo:
            for rec in parser.results:
                serializer.write(rec, fo)
        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)


class TestPnas(unittest.TestCase):

    def setUp(self):
        self.stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata')
        self.patcher = patch('requests.get')
        self.requests_mock = self.patcher.start()

    def test_pnas_parser(self):
        mock_infile = os.path.join(self.stubdata_dir, 'input', 'pnas_feedparser.resp')
        mock_html_file = os.path.join(self.stubdata_dir, 'input', 'pnas_resp.html')
        mock_data = open(mock_infile, open_mode_u).read()
        mock_html = open(mock_html_file, open_mode_u).read()
        self.requests_mock.return_value.text = MockResponse(mock_html)
        feed = json.loads(mock_data)
        for _item in feed['entries']:
            absURL = _item['link']
            parser = pnas.PNASParser()
            output = parser.parse(absURL)

        serializer = classic.Tagged()
        test_outfile = os.path.join(self.stubdata_dir, 'serialized', 'test_pnas.tag')
        if sys.version_info > (3,):
            standard_outfile = os.path.join(self.stubdata_dir, 'serialized', 'python3', 'pnas.tag')
        else:
            standard_outfile = os.path.join(self.stubdata_dir, 'serialized', 'pnas.tag')
        try:
            os.remove(test_outfile)
        except Exception as err:
            pass
        with open(test_outfile, 'w') as fo:
            serializer.write(output, fo)

        result = filecmp.cmp(test_outfile, standard_outfile)
        self.assertEqual(result, True)
        os.remove(test_outfile)
