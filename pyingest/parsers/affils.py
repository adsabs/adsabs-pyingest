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
    Affiliation string parser, to deal with email, ORCID tags
    """

    def __init__(self, input_string):
        self.original_string = input_string
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


    def find_untagged_email(self):
        email_split = self.original_string.split()
        email = u''
        email_list = []
        for e in email_split:
            at = e.split('@')
            if len(at) > 1 and re.search('\w\.\w',at[1]):
#               email = e
                email_list.append(e)
            email = ', '.join(email_list)
        email = re.sub(';','',email)
        return email


    def parse(self):
#       try:
            orcid = self.find_orcid_tag()
            email = self.find_email_tag()
            new_string = self.input_tagged.p.extract().text
            new_string = re.sub(' ;','',new_string)
            if orcid != u'':
                new_string = new_string + '; ' + unicode(orcid)
            if email != u'': 
                new_string = new_string + '; ' + unicode(email) 
            else:
                email = self.find_untagged_email()
                new_string = re.sub(email,'',new_string)
                new_string = new_string + '; ' + unicode(email) 
            new_string = re.sub(' ;','',new_string)
            return new_string
#       except:
#           return self.original_string


def __main__():



    print "\nONE:"
    aff = "Harvard-Smithsonian Center for Astrophysics; <EMail>matthew.templeton@cfa.harvard.edu</EMail>; <ID system='ORCiD'>0000-0000-1234-5678</ID>; State Key Laboratory for Stamp Collecting, Ministry of Silly Walks, University of Basketweaving" 

    parser = AffiliationParser(aff)
    new_string = parser.parse()

    print "\n"
    print new_string
    print "----------------------\n"



    print "\nTWO:"
    aff = "Harvard-Smithsonian Center for Astrophysics; <EMAIL>matthew.templeton@cfa.harvard.edu</EMAIL>; <ORCID>0000-0000-1234-5678</ORCID>; State Key Laboratory for Stamp Collecting, Ministry of Silly Walks, University of Basketweaving" 

    parser = AffiliationParser(aff)
    new_string = parser.parse()

    print "\n"
    print new_string
    print "----------------------\n"



    print "\nTHREE:"
    aff = "Harvard-Smithsonian Center for Astrophysics; matthew.templeton@cfa.harvard.edu; <ORCID>0000-0000-1234-5678</ORCID>; State Key Laboratory for Stamp Collecting, Ministry of Silly Walks, University of Basketweaving" 

    parser = AffiliationParser(aff)
    new_string = parser.parse()

    print "\n"
    print new_string
    print "----------------------\n"



    print "\nFOUR:"
    aff = "CfA @ Harvard; matthew.templeton@cfa.harvard.edu; <ORCID>0000-0000-1234-5678</ORCID>; State Key Laboratory for Stamp Collecting, Ministry of Silly Walks, University of Basketweaving" 

    parser = AffiliationParser(aff)
    new_string = parser.parse()

    print "\n"
    print new_string
    print "----------------------\n"



    print "\nFIVE:"
    aff = "CfA@Harvard; matthew.templeton@cfa.harvard.edu; <ORCID>0000-0000-1234-5678</ORCID>; State Key Laboratory for Stamp Collecting, Ministry of Silly Walks, University of Basketweaving" 

    parser = AffiliationParser(aff)
    new_string = parser.parse()

    print "\n"
    print new_string
    print "----------------------\n"



    print "\nSIX:"
    aff = "lol butts; <ORCID>0000-0000-1234-5678</ORCID>; brandewijn@gmail.com; State Key Laboratory for Stamp Collecting, Ministry of Silly Walks, University of Basketweaving; CfA@Harvard; foo@bar.baz" 

    parser = AffiliationParser(aff)
    new_string = parser.parse()

    print "\n"
    print new_string
    print "----------------------\n"


if __name__ == '__main__':
    __main__()
