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
