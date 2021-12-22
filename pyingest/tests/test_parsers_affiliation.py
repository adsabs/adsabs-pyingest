"""
Test parsers
"""
from __future__ import print_function

import unittest
import sys

from pyingest.parsers.affils import AffiliationParser


if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'


class TestAffiliationParser(unittest.TestCase):

    def setUp(self):
        self.aff_str = ['Canadian Institute for Theoretical Astrophysics, University of Toronto, 60 St. George Street, Toronto, ON M5S 1A7, Canada; testing.fun@cita.utoronto.ca; 0000-0000-0000-1234',
                        'Canadian Institute for Theoretical Astrophysics, University of Toronto, 60 St. George Street, Toronto, ON M5S 1A7, Canada; <EMAIL>testing.fun@cita.utoronto.ca</EMAIL>; <id system="ORCID">0000-0000-0000-1234</id>',
                        'fnord@fnord.com ; This is not an affiliation.; This is: CITA, 60 whatevs, Toronto, ON, CA',
        ]

        self.out_str = ['Canadian Institute for Theoretical Astrophysics, University of Toronto, 60 St. George Street, Toronto, ON M5S 1A7, Canada; 0000-0000-0000-1234; testing.fun@cita.utoronto.ca',
                        'Canadian Institute for Theoretical Astrophysics, University of Toronto, 60 St. George Street, Toronto, ON M5S 1A7, Canada; <id system="ORCID">0000-0000-0000-1234</id>; <email>testing.fun@cita.utoronto.ca</email>',
                        'This is not an affiliation.; This is: CITA, 60 whatevs, Toronto, ON, CA; fnord@fnord.com',
        ]

    # Test 3
    def test_simple_parse(self):
        for _in, _out in zip(self.aff_str, self.out_str):
            affil = AffiliationParser(_in)
            output_field = affil.parse()
            # print(_in)
            # print(output_field)
            self.assertEqual(_out, output_field)
