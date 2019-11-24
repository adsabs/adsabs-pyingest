import os
import sys
import re
import logging
import bs4
from default import BaseBeautifulSoupParser
from namedentities import named_entities, unicode_entities
import nameparser
from adsputils import u2asc

class AffiliationParser(BaseBeautifulSoupParser):
    """
    Affiliation string parser, to deal with email, orcid tags
    """

    def __init__(self, input_string):
        self.input_tagged = self.resource_dict(input_string)
        pass

    def resource_dict(self, aff_string, **kwargs):
        d = self.bsstrtodict(aff_string, **kwargs)
        return d

    def find_orcid_tag(self):
        orcid = u''
        try:
            if not self.input_tagged.orcid:
                if not self.input_tagged.id:
                    orcid = u''
                else:
                    id_dict = self.input_tagged.id.attrs
                    if id_dict['system'].lower() == 'orcid':
                        orcid = self.input_tagged.id.extract()
                    else:
                        orcid = u''
            else:
                orcid = self.input_tagged.orcid.extract()
        except:
            orcid = u''
        return orcid


    def find_email_tag(self):
        email = u''
        try:
            if not self.input_tagged.email:
                email = u''
            else:
                email = self.input_tagged.email.extract()
        except:
            email = u''
        return email


    def parse(self):
        orcid = self.find_orcid_tag()
        email = self.find_email_tag()
        new_string = self.input_tagged.p.extract().text
        new_string = re.sub(' ;','',new_string)
        if email != u'': 
            new_string = new_string + '; ' + unicode(email) 
        if orcid != u'':
            new_string = new_string + '; ' + unicode(orcid)
        return new_string


#def __main__():
#    aff = "Harvard-Smithsonian Center for Astrophysics; <EMail>matthew.templeton@cfa.harvard.edu</EMail>; <ID system='ORCiD'>0000-0000-1234-5678</ID>; State Key Laboratory for Stamp Collecting, Ministry of Silly Walks, University of Basketweaving" 
#
#    parser = AffiliationParser(aff)
#    new_string = parser.parse()
#
#    print new_string
#
#    aff = "Harvard-Smithsonian Center for Astrophysics; <fnord>matthew.templeton@cfa.harvard.edu</fnord>; <orcid>0000-0000-1234-5678</orcid>; State Key Laboratory for Stamp Collecting, Ministry of Silly Walks, University of Basketweaving" 
#
#    parser = AffiliationParser(aff)
#    new_string = parser.parse()
#
#    print new_string
#
#
#if __name__ == '__main__':
#    __main__()
