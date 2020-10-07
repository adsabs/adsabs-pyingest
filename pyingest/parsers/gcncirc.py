from __future__ import print_function
from __future__ import absolute_import
import sys
import json
import re
import logging
from pyingest.config.utils import u2asc
from .default import DefaultParser
from .author_names import AuthorNames
from .entity_convert import EntityConverter

head_dict = {'TITLE:': 'journal', 'NUMBER:': 'volume', 'SUBJECT:': 'title',
             'DATE:': 'pubdate', 'FROM:': 'email'
             }


class GCNCParser(DefaultParser):

    def __init__(self, data):
        # econv = EntityConverter()
        # econv.input_text = data
        # econv.convert()
        # self.raw = econv.output_text
        self.raw = data
        self.data_dict = dict()

    def make_pubdate(self):
        input_date = self.data_dict['pubdate']
        yymmdd = input_date.split('/')
        if int(yymmdd[0]) > 50:
            year = '19' + yymmdd[0]
        else:
            year = '20' + yymmdd[0]
        pubdate = year + '/' + yymmdd[1]
        self.data_dict['pubdate'] = pubdate

    def make_bibcode(self):
        year = self.data_dict['pubdate'][0:4]
        bibcode = 'GCN.'
        self.data_dict['volume'] = self.data_dict['volume'].ljust(5, '.')
        volume = self.data_dict['volume'].ljust(9, '.') + '1'
        try:
            init = u2asc(self.data_dict['authors'][0][0])
        except Exception as err:
            print ("Problem generating author initial")
            init = '.'
        self.data_dict['bibcode'] = year + bibcode + volume + init

    def make_publication(self):
        base_string = 'GRB Coordinates Network, Circular Service, No. '
        self.data_dict['publication'] = base_string + self.data_dict['volume']
        self.data_dict['page'] = '1'

    def split_authors_abstract(self):
        # This could be used to extract affils and apply them to authors,
        # but the process of doing so is unwieldy.  I'm leaving code that
        # was my initial try but commented out.
        body = self.data_dict['abstract']
        while body[0] == '':
            body.pop(0)
        auths = []
        affils = []
        while body[0] != '' and ':' not in body[0]:
            auths.append(body.pop(0).strip())
        auths.append(body.pop(0).strip())
        auth_delimiter = u'| '

        auth_string = ' '.join(auths)

        auth_string = re.sub(r'\s+\((.*?)\)', ',', auth_string)
        auth_string = re.sub(r'[ ,]and\s', ',', auth_string)
        auth_string = re.sub(r'on behalf of', ',', auth_string)
        auth_string = re.sub(r'reports?', ',', auth_string)
        auth_string = re.sub(r'\s?:', '', auth_string)
        auth_string = re.sub(r',?\s+,', ',', auth_string)

        auth_array = [s.strip() for s in auth_string.split(',')]
        auth_array = list([a for a in auth_array if len(a) > 3])
        # auth_string = u'; '.join(auth_array)
        auth_string = auth_delimiter.join(auth_array)
        auth_mod = AuthorNames()
        # self.data_dict['authors'] = auth_mod.parse(auth_string)
        self.data_dict['authors'] = auth_mod.parse(auth_string, delimiter=auth_delimiter)
        self.data_dict['authors'] = re.sub(r'\| ', u';', self.data_dict['authors'])

    def parse(self):

        self.data_dict = {}
        # Start by looking at the Circular line by line...
        try:
            gdata = self.raw.split('\n')

        # Header is fixed format and five lines long...
            head = gdata[0:5]
            for l in head:
                lfix = l.replace(' ', '\t', 1)
                lparts = lfix.split('\t')
                self.data_dict[head_dict[lparts[0]]] = lparts[1].strip()
            # Now you need to split the authors from the abstract.
            # This should work in *most* cases, maybe not all,
            # especially from older (pre-2016) Circulars
            self.data_dict['abstract'] = gdata[5:]
            self.split_authors_abstract()
            # Authors and abstract content should now be defined

            # If you want to try and keep fixed formatting
            # (e.g. for tables), use '\n' for the join character
            abstract_new = ' '.join(self.data_dict['abstract'])
            self.data_dict['abstract'] = abstract_new.strip()

            # Extract pubdate from the header date
            self.make_pubdate()

            # Create the bibcode from circular info
            self.make_bibcode()

            # Make the publication string
            self.make_publication()

            # Pass the necessary fields through EntityConverter
            ec_fields = ['authors', 'abstract', 'title']
            econv = EntityConverter()
            for ecf in ec_fields:
                econv.input_text = self.data_dict[ecf]
                econv.convert()
                self.data_dict[ecf] = econv.output_text

        except Exception as err:
            self.data_dict['raw'] = self.raw
            self.data_dict['error'] = err

        return self.data_dict
