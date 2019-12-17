import sys
import json
import re
import logging
from default import DefaultParser

head_dict = {'TITLE:': 'journal', 'NUMBER:': 'page', 'SUBJECT:': 'title',
             'DATE:': 'pubdate', 'FROM:': 'author'
            }



class GCNCParser(DefaultParser):

    def __init__(self, data):
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
        bibcode = 'GCN..'
        page = self.data_dict['page'].rjust(9,'.')
        init = '.'
        self.data_dict['bibcode'] = year + bibcode + page + init

    def parse_first_author(self):
        x = 'x'

    def split_authors_abstract(self):
        body = self.data_dict['abstract']
        while body[0] == '':
            body.pop(0)
        auths = []
        affils = []
        while body[0] != '' and ':' not in body[0]:
            auths.append(body.pop(0).strip())
        auths.append(body.pop(0).strip())
        auth_string = ' '.join(auths)
        auth_array = auth_string.split(',')
        print "AUTHORS: ",auth_array
        for a in auth_array:
            aff = re.search(r'\((.*?)\)',a).group(1)
            # aff = a[a.find("(")+1:a.find(")")]
            # print "auth:",a
#           print "lol aff:",aff

    def parse(self):

        self.data_dict = {}
        try:
            gdata = self.raw.split('\n')

            head = gdata[0:5]
            for l in head:
                lfix = l.replace(' ','\t',1)
                lparts = lfix.split('\t')
                self.data_dict[head_dict[lparts[0]]] = lparts[1].strip()
            self.data_dict['abstract'] = gdata[5:]
            self.split_authors_abstract()
#           body = [x for x in gdata[5:] if x != '']
#           self.data_dict['abstract'] = '<pre>' + '\n'.join(body) + '<\\pre>'
        except Exception, err:
            self.data_dict['raw'] = self.raw
            self.data_dict['error'] = err
        self.make_pubdate()
        self.make_bibcode()
        return self.data_dict
