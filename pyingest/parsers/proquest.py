import os
import re
import pymarc
from pyingest.config import config
from pyingest.parsers.author_names import AuthorNames
from default import DefaultParser

# For the MARC2.1 standard guide, see:
# https://www.loc.gov/marc/bibliographic/
# Note that records from ProQuest cant be loaded correctly by 
# pymarc>=2.9.2 because they often have more than two subfields
# (which is not the standard).  You need to install pymarc<=2.9.1

class ProQuestParser(DefaultParser):

    def __init__(self, filename):
        marc_input_file = config.PROQUEST_BASE_PATH + filename
        oa_input_file = marc_input_file.replace('.UNX','_OpenAccessTitles.csv')
        self.records = open(marc_input_file).read().strip().split('\n')
        oa_input_data = open(oa_input_file).read().strip().split('\n')
        self.oa_pubnum = list()
        #for line in oa_input_data:
        #    entries = line.split(',')
        #    self.oa_pubnum.append(str(int(entries[0])))
        self.results = list()

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
                output_metadata['origin'] = datasource

                # read each record into a pymarc object
                reader = pymarc.MARCReader(r, to_unicode=True)
                record = reader.next()

                # ProQuest ID (001)
                proqid = record['001'].value()
                proqid_number = proqid[3:]

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
                except:
                    isbn = ''

                # Author (100)
                try:
                    author = re.sub('\.$','',record['100']['a'].strip())
                    author = auth_parse.parse(author)
                except Exception, err:
                    print "doh:",err
                    author = ''
            
                # Title
                try:
                    title = record['245']['a']
                except:
                    title = ''

                # Page length
                try:
                    npage = record['300']['a']
                except:
                    npage = ''

                # Source and Advisor

                # Abstract (multiline field: 520)
                abstract = ''
                for l in record.get_fields('520'):
                    try:
                        abstract += ' ' + l.value().strip()
                    except:
                        pass
                abstract = abstract.strip()
             

                # Affil
                affil=''
                try:
                    affil = record['710']['a'].rstrip('.')
                except:
                    pass
                else:
                    try:
                        a2 = record['710']['b'].rstrip('.')
                    except Exception, err:
                        pass
                    else:
                        affil = a2 + ', ' + affil


                output_metadata['authors'] = author
                output_metadata['affiliations'] = [affil]
                output_metadata['title'] = title
                output_metadata['abstract'] = abstract


            except Exception, err:
                print("Record skipped, MARC parsing failed: %s" % err)
            else:
                self.results.append(output_metadata)

        return
