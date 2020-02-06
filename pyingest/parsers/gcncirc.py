import sys
import json
import re
import logging
from default import DefaultParser
from author_names import AuthorNames
from entity_convert import EntityConverter

head_dict = {'TITLE:': 'journal', 'NUMBER:': 'page', 'SUBJECT:': 'title',
             'DATE:': 'pubdate', 'FROM:': 'email'
            }



class GCNCParser(DefaultParser):

    def __init__(self, data):
        econv = EntityConverter()
        econv.input_text = data
        econv.convert()
        self.raw = econv.output_text
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
        if int(self.data_dict['page']) < 10000:
            self.data_dict['page'] = '.' + self.data_dict['page']
        page = self.data_dict['page'].ljust(9,'.') + '1'
        try:
            init = self.data_dict['authors'][0][0]
        except Exception, err:
            print ("No author initial")
            init = '.'
        self.data_dict['bibcode'] = year + bibcode + page + init

    def make_publication(self):
        base_string = 'GRB Coordinates Network, Circular Service, No. '
        self.data_dict['publication'] = base_string + self.data_dict['page']
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

        auth_string = ' '.join(auths)

        # auth_parens_loc = [(m.start(),m.end()) for m in re.finditer(r'\((.*?)\)',auth_string)]
        # auth_parens.reverse()
        # auth_array = auth_string.split(',')
        # auth_author_loc = [auth_string.find(s) for s in auth_array]
        # print auth_author_loc
        # print auth_parens_loc
        # auth_loc = [(m.start(),m.end()) for m in [a for a in auth_array]]
        # print auth_parens,auth_loc
        # auth_array = [m.strip() for m in auth_array]


        # print('\n\n\n\n')
        # print(auth_string)
        auth_string = re.sub(r'\s+\((.*?)\)\s+', ',', auth_string)
        auth_string = re.sub(r'[ ,]and\s', ',', auth_string)
        auth_string = re.sub(r'on behalf of',',',auth_string)
        auth_string = re.sub(r'reports?', ',', auth_string)
        auth_string = re.sub(r'\s?:','', auth_string)
        auth_string = re.sub(r',\s+,',',', auth_string)
        
        # print('\n')
        # print(auth_string)

        auth_array = [s.strip() for s in auth_string.split(',')]
        auth_array = list(filter(lambda a: len(a) > 3, auth_array))
        # self.data_dict['authors'] = auth_array
        auth_string = '; '.join(auth_array)
        auth_mod = AuthorNames()
        self.data_dict['authors'] = auth_mod.parse(auth_string)
        
        # for a in auth_array:
            # if len(a) <= 3:
                # auth_array.remove(a)
        # print auth_array
        # print '\n\n'
        

    def parse(self):

        self.data_dict = {}
        # Start by looking at the Circular line by line...
        try:
            gdata = self.raw.split('\n')

        # Header is fixed format and five lines long...
            head = gdata[0:5]
            for l in head:
                lfix = l.replace(' ','\t',1)
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
            abstract_new= ' '.join(self.data_dict['abstract'])
            self.data_dict['abstract'] = abstract_new.strip()

            # Extract pubdate from the header date
            self.make_pubdate()

            # Create the bibcode from circular info
            self.make_bibcode()

            # Make the publication string
            self.make_publication()

        except Exception, err:
            self.data_dict['raw'] = self.raw
            self.data_dict['error'] = err


        return self.data_dict

# def main():
#
#     flist = ['23456.gcn3','23457.gcn3','23458.gcn3','25321.gcn3','9999.gcn3','98765.gcn3']
#     basedir = '/Users/mtempleton/Projects/GCN_Parser/gcn3/'
#     for f in flist:
#         f2 = basedir + f
#         with open(f2,'rU') as fg:
#             d = fg.read()
#         x = GCNCParser(d)
#         y = x.parse()
#
#
# if __name__ == '__main__':
#    main()
