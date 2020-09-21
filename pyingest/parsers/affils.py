from __future__ import print_function
import re
from .default import BaseBeautifulSoupParser


class AffiliationParser(BaseBeautifulSoupParser):
    """
    Affiliation string parser, to deal with email, ORCID tags
    """

    def __init__(self, input_string):
        self.original_string = input_string
        self.input_tagged = self.resource_dict(input_string)

    def resource_dict(self, aff_string, **kwargs):
        _d = self.bsstrtodict(aff_string, **kwargs)
        return _d

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
            orcid = unicode(orcid)
        except Exception as err:
            print("AffiliationParser: problem finding orcid tag:", err)
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
        except Exception as err:
            print("AffiliationParser: problem finding email tag:", err)
            email = u''
        return email

    def find_untagged_email(self):
        email_split = self.original_string.split(' ')
        email = u''
        email_list = []
        for _e in email_split:
            _at = _e.split('@')
            if len(_at) > 1 and re.search(r'\w\.\w', _at[1]):
                email_list.append(_e)
            email = ', '.join(email_list)
        email = re.sub(';', '', email)
        return email

    def parse(self):
        try:
            orcid = self.find_orcid_tag()
            email = self.find_email_tag()
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
        except Exception as err:
            print("AffiliationParser: PARSING FAILED:", err)
            return self.original_string
