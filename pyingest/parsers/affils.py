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
        except Exception, err:
            orcid = u''
        self.original_string = re.sub(orcid, '', self.original_string)
        return orcid

    def find_email_tag(self):
        email = u''
        try:
            if not self.input_tagged.email:
                email = u''
            else:
                email = self.input_tagged.email.extract()
        except Exception, err:
            email = u''
        return email

    def find_untagged_email(self):
        email_split = self.original_string.split(' ')
        email = u''
        email_list = []
        for e in email_split:
            at = e.split('@')
            if len(at) > 1 and re.search(r'\w\.\w', at[1]):
                email_list.append(e)
            email = ', '.join(email_list)
        email = re.sub(';', '', email)
        return email

    def parse(self):
        try:
            orcid = self.find_orcid_tag()
            email = self.find_email_tag()
            # new_string = self.input_tagged.p.extract().text
            new_string = self.input_tagged.extract().text
            new_string = re.sub(' ;', '', new_string)
            if orcid != u'':
                new_string = new_string + '; ' + unicode(orcid)
            if email != u'':
                new_string = new_string + '; ' + unicode(email)
            else:
                email = self.find_untagged_email()
                new_string = re.sub(email, '', new_string)
                new_string = new_string + '; ' + unicode(email)
            new_string = re.sub(' ;', '', new_string)
            new_string = new_string.strip()
            new_string = new_string.strip(';')
            new_string = new_string.strip()
            return new_string
        except Exception, err:
            print("problem...")
            return self.original_string


def __main__():

    aff1 = "brandewijn@gmail.com; ABC Inc."
    aff2 = "ABC Inc. (brandewijn@gmail.com)"
    aff3 = "ABC Inc.: brandewijn@gmail.com; DEF Inc.: foo@bar.baz"
    aff4 = "ABC Inc. <email>brandewijn@gmail.com</email>; DEF Inc. <email>foo@bar.baz</email>"
    aff5 = "brandewijn@gmail.com"
    affs = [aff1, aff2, aff3, aff4, aff5]

    for a in affs:

        parser = AffiliationParser(a)
        new_string = parser.parse()

        print "----------------------\n"
        print "input string:", a
        print "\n"
        print "outpt string:", new_string
        print "----------------------\n"


if __name__ == '__main__':
    __main__()
