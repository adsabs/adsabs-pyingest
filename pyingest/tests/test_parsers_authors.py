"""
Test parsers
"""
from __future__ import print_function

import unittest
import sys

from pyingest.parsers.author_names import AuthorNames

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'


class TestAuthorNames(unittest.TestCase):

    def setUp(self):
        self.author_names = AuthorNames()
        self.authors_str = u"robert white smith; m. power; maria antonia de la paz; bla., bli.; the collaboration: john stuart; collaboration, gaia; john; github_handle;;.."

    # Test 4
    def test_default_author_names(self):
        # expected_authors_str = u"white smith, robert; power, m.; de la paz, maria antonia; bla., bli.; Collaboration; stuart, john; Collaboration, Gaia; John; github_handle; Unknown, Unknown; .."
        expected_authors_str = u"white smith, robert; power, m.; de la paz, maria antonia; bla., bli.; Collaboration; stuart, john; Collaboration, gaia; john; github_handle; ; .."
        # Default
        corrected_authors_str = self.author_names.parse(self.authors_str)
        self.assertEqual(corrected_authors_str, expected_authors_str)

    # Test 5
    def test_normalize_author_names(self):
        corrected_authors_str = u"white smith, Robert; power, M; de la paz, Maria Antonia; bla, Bli; Collaboration; stuart, John; Collaboration, gaia; john; github_handle; ; "
        expected_normalized_authors_str = u"white smith, R; power, M; de la paz, M A; bla, B; Collaboration; stuart, J; Collaboration gaia; john; github_handle; ; "
        # Normalize
        normalized_authors_str = self.author_names._normalize(corrected_authors_str)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)
        normalized_authors_str = self.author_names.parse(self.authors_str, normalize=True)
        self.assertEqual(normalized_authors_str, expected_normalized_authors_str)

    # Test 6
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

    # Test 7
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

    # Test 8
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

    # Test 9
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

    # Test 10
    def test_dutch_people(self):
        input_names = u"Berg, Imme van den; Imme van den Berg; 't Hooft, Gerard; Hooft, Gerard 't; Hooft, Bas van't; van't Hooft, Bas"
        expected_output_names = u"van den Berg, I; van den Berg, I; 't Hooft, G; 't Hooft, G; van't Hooft, B; van't Hooft, B"
        output_names = self.author_names.parse(input_names, normalize=True)
        self.assertEqual(output_names, expected_output_names)
