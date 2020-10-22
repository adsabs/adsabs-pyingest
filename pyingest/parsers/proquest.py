from __future__ import print_function
from __future__ import absolute_import
import re
import sys
if sys.version_info > (3,) or 'unittest' in sys.modules.keys():
    import pymarc
else:
    print('Error: need to manually install an older version of pymarc for ingestion. '
          'Run the following: "pip install pymarc<=2.9.1"')
from pyingest.config import config
from pyingest.parsers.author_names import AuthorNames
from .default import DefaultParser


# For the MARC2.1 standard guide, see:
# https://www.loc.gov/marc/bibliographic/
# Note that records from ProQuest cant be loaded correctly by 
# pymarc>=2.9.2 because they often have more than two subfields
# (which is not the standard).  You need to install pymarc<=2.9.1

class ProQuestParser(DefaultParser):

    def __init__(self, filename):
        marc_input_file = config.PROQUEST_BASE_PATH + filename
        oa_input_file = marc_input_file.replace('.UNX', '_OpenAccessTitles.csv')
        self.records = open(marc_input_file).read().strip().split('\n')
        oa_input_data = open(oa_input_file).read().strip().split('\n')
        self.oa_pubnum = list()
        for line in oa_input_data:
            entries = line.split(',')
            try:
                self.oa_pubnum.append(str(int(entries[0])))
            except Exception as err:
                pass
        self.results = list()

    def get_db(self, rec):
        subjects = []
        databases = []
        try:
            for chunk in rec.get_fields('650'):
                if chunk['a'] not in subjects:
                    cat = re.sub('\\.$', '', chunk['a'])
                    try:
                        db = config.PROQUEST_TO_DB.get(cat, 'PHY')
                        if 'physics' in cat.lower():
                            db = 'PHY'
                        if 'astronomy' in cat.lower() or 'astroph' in cat.lower():
                            db = 'AST'
                        if db not in databases:
                            databases.append(db)
                    except Exception as err:
                        # if cat not in missingCats:
                            # missingCats.append(cat)
                        # sys.stderr.write("Could not find DB for category: %s\n"%cat)
                        pass
                    subjects.append(cat)
        except Exception as err:
            pass
        return databases, subjects

    def parse(self):

        b2p = config.PROQUEST_BIB_TO_PUBNUM
        oa_base = config.PROQUEST_OA_BASE
        url_base = config.PROQUEST_URL_BASE

        auth_parse = AuthorNames()

        for r in self.records:
            output_metadata = dict()

            try:
                # This is parsing ProQuest / UMI data -- add to origin
                datasource = 'UMI'

                jfield = ['ProQuest Dissertations And Thesis']

                # read each record into a pymarc object
                if sys.version_info > (3,):
                    reader = pymarc.MARCReader(r.encode('utf-8'), to_unicode=True)
                else:
                    reader = pymarc.MARCReader(r, to_unicode=True)
                record = next(reader)

                # ProQuest ID (001)
                proqid = record['001'].value()
                pubnr = proqid.replace('AAI', '')

                # MARC 2.1 fixed length data elements (005)
                flde = record['005'].value()
                # Publication Year
                pubyear = flde[0:4]
                # Defense Year
                def_year = flde[7:11]
                # Language
                language = flde[35:38]

                # ISBN (020)
                try:
                    isbn = record['020']['a']
                except Exception as err:
                    isbn = ''

                # Author (100)
                try:
                    author = re.sub('\\.$', '', record['100']['a'].strip())
                    # author = auth_parse.parse(author)
                except Exception as err:
                    author = ''
            
                # Title
                try:
                    title = re.sub('\\.$', '', record['245']['a'].strip())
                except Exception as err:
                    title = ''

                # Page length
                try:
                    npage = record['300']['a']
                except Exception as err:
                    npage = ''

                # Source
                try:
                    school = record['502']['a']
                except Exception as err:
                    pass
                else:
                    jfield.append(school)
                jfield.append('Publication Number: %s' % re.sub('AAI', 'AAT ', proqid))
                if isbn:
                    jfield.append('ISBN: %s' % isbn)
               
                try:
                    publsh = record['500']['a']
                except Exception as err:
                    pass
                else:
                    jfield.append(publsh)

                if npage:
                    jfield.append(npage)

                # Abstract (multiline field: 520)
                abstract = ''
                for l in record.get_fields('520'):
                    try:
                        abstract += ' ' + l.value().strip()
                    except Exception as err:
                        pass
                abstract = abstract.strip()

                # ADS Collection/Database
                (databases, subjects) = self.get_db(record)

                # Affil
                affil = ''
                try:
                    affil = record['710']['a'].rstrip('.')
                except Exception as err:
                    pass
                else:
                    try:
                        a2 = record['710']['b'].rstrip('.')
                    except Exception as err:
                        pass
                    else:
                        affil = a2 + ', ' + affil

                # Advisor
                advisor = []
                comments = []
                try:
                    for e in record.get_fields('790'):
                        if e['e']:
                            advisor.append(e['a'])
                    if advisor:
                        comments.append('Advisor: %s' % advisor[0])
                except Exception as err:
                    pass

                # Pubdate
                try:
                    pubdate = record['792']['a']
                except Exception as err:
                    pubdate = ''

                # Language
                lang = []
                try:
                    for l in record.get_fields('793'):
                        ln = l.value().strip() 
                        lang.append(ln)
                except Exception as err:
                    pass

                # properties
                properties = dict()
                if pubnr in self.oa_pubnum:
                    properties['OPEN'] = 1
                    # new_proqid = proqid.replace('AAI','AAT ')
                    url = oa_base % pubnr
                else:
                    url = url_base % pubnr
                properties['ELECTR'] = url

                output_metadata['source'] = datasource
                output_metadata['authors'] = author
                output_metadata['affiliations'] = [affil]
                output_metadata['title'] = title
                output_metadata['abstract'] = abstract
                output_metadata['publication'] = '; '.join(jfield)
                if pubdate:
                    output_metadata['pubdate'] = "%s" % pubdate
                if databases:
                    output_metadata['database'] = databases
                if comments:
                    output_metadata['comments'] = comments
                # if keywords:
                    # output_metadata['keywords'] = keywords
                if lang:
                    output_metadata['language'] = lang
                if subjects:
                    output_metadata['subjectcategory'] = subjects
                if properties:
                    output_metadata['properties'] = properties

            except Exception as err:
                print("Record skipped, MARC parsing failed: %s" % err)
            else:
                self.results.append(output_metadata)

        return
