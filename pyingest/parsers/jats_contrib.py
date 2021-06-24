import re
from collections import OrderedDict

class JATSContribException(Exception):
    pass


class JATSContribs(object):


    def __init__(self, soup=None):
        self.regex_spcom = re.compile(r'\s+,')
        self.regex_multisp = re.compile(r'\s+')
        self.regex_email = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+')
        self.soup = soup
        self.collab = {}
        self.auth_list = []
        self.xref_dict = OrderedDict()
        self.email_xref = OrderedDict()
        self.output = []
        pass

    def _name_to_ads(self, name):
        '''
        conv a flded name (surname/given) to ADS text name ('surname, given')
        '''
        try:
            # NOTE: using 'contents[0]' will strip out any markup in the object
            # surname = name.find('surname').contents[0]
            # given = name.find('given-names').contents[0]
            surname = name.find('surname').text
            given = name.find('given-names').text
            ads_name = str(surname) + ', ' + str(given)
            return ads_name
        except Exception as noop:
            # print('this is a problem, add logging/exception')
            return

    def _match_xref(self):
        for a in self.auth_list:
            try:
                for item in a['xaff']:
                    item = re.sub(r'\s+',',',item)
                    xi = re.split(',',item)
                    for x in xi:
                        try:
                            a['aff'].append(self.xref_dict[x])
                        except Exception as err:
                            # print('missing key in xaff!', err)
                            pass

                    # if you found any emails in an affstring, add them
                    # to the email field
                    if item in self.email_xref:
                        a['email'].append(self.email_xref[item])

                # Check for 'ALLAUTH' affils (global affils without a key), 
                # and assign them to all authors
                if 'ALLAUTH' in self.xref_dict:
                    a['aff'].append(self.xref_dict['ALLAUTH'])
            except Exception as noop:
                pass

            try:
                for item in a['xemail']:
                    try:
                        a['email'].append(self.xref_dict[item])
                    except Exception as err:
                        # print('missing key in xemail!',err)
                        pass
            except Exception as err:
                pass

    def _fix_email(self, email):
        email_new = []
        for em in email:
            if ' ' in em:
                for e in em.strip().split():
                    if '@' in e:
                        email_new.append(e.strip())
            else:
                if '@' in em:
                    email_new.append(em.strip())
        return list(dict.fromkeys(email_new))

    def _fix_orcid(self, orcid):
        orcid_new = []
        for orc in orcid:
            osplit = orc.strip().split()
            for o in osplit:
                o = o.rstrip('/').split('/')[-1]
                orcid_new.append(o)
        return list(dict.fromkeys(orcid_new))

    def _fix_affil(self,affstring):
        aff_list = affstring.split(';')
        new_aff = []
        emails = []
        for a in aff_list:
            if self.regex_email.match(a.strip()):
                emails.append(a.strip())
            else:
                if a.strip():
                    new_aff.append(a.strip())

        newaffstr = '; '.join(new_aff)
        return (newaffstr, emails)



    def _refield(self):
        out_auth = []
        out_aff = []
        email = None
        orcid = None
        for a in self.auth_list:
            try:
                name = a['name']
            except Exception as err:
                # this shouldn't happen, add an exception
                pass
            else:
                try:
                    aff = a['aff']
                    email = self._fix_email(a['email']) or None
                    orcid = self._fix_orcid(a['orcid']) or None
                    aff_new = '; '.join(aff)
                    if orcid:
                        orcid = '; '.join(orcid).strip()
                        orcid = '; <ID system="ORCID">' + orcid + '</ID>'
                        aff_new = aff_new + orcid
                    if email:
                        email = '; '.join(email).strip()
                        email = '<EMAIL>' + email + '</EMAIL>'
                        aff_new = aff_new + ' ' + email
                    aff_new = self.regex_spcom.sub(',',aff_new)
                    aff_new = self.regex_multisp.sub(' ',aff_new)
                except Exception as noop:
                    aff_new = ''
                out_auth.append(name.strip())
                out_aff.append(aff_new)

        # sanity check:
        if len(out_auth) != len(out_aff):
            # this should be a try/except...
            print('length mismatch in auth-affil data!')
        self.output = {'authors': out_auth, 'affiliations': out_aff}

    def _decompose(self, soup=None, tag=None):
        try:
            for element in soup(tag):
                element.decompose()
        except Exception as noop:
            pass
        return soup


    def parse(self):
        try:
            # BEGIN
            art_meta = self.soup

            # De-label everything:
            try:
                art_meta = self._decompose(soup=art_meta, tag='label')
            except Exception as noop:
                pass

            # JATS puts author data in <contrib-group>, giving individual
            # authors in each <contrib>
            try:
                art_contrib_group = art_meta.find('contrib-group').extract()
            except Exception as noop:
                print('If you see this, you have a problem...', noop)
                pass
            else:
                contrib_raw = art_contrib_group.find_all('contrib')

                for a in contrib_raw:
                    auth = {}
                    l_correspondent = False

                    # note: IOP, APS get affil data within each contrib block,
                    #       OUP, AIP, Springer, etc get them via xrefs.
                    if a['contrib-type'] == 'collab':
                        collab = a.find('collab')
                        try:
                            collab_name = collab.contents[0]
                        except Exception as err:
                            pass
                        else:
                            self.collab = {'name': collab_name, 
                                           'aff': [],
                                           'xaff': [],
                                           'xemail': [],
                                           'email': [],
                                           'corresp': False
                                          }
                    elif a['contrib-type'] == 'author':
                        if a.find('collab') is not None:
                            try:
                                collab_name = collab.find('institution').text
                            except Exception as noop:
                                pass
                            else:
                                self.collab = {'name': collab_name, 
                                               'aff': [],
                                               'xaff': [],
                                               'xemail': [],
                                               'email': [],
                                               'corresp': False
                                              }
                                try:
                                    collab_affil = collab.find('address').text
                                except Exception as noop:
                                    pass
                                else:
                                    self.collab['aff'] = collab_affil
                        else:
                            # corresponding author?
                            try:
                                if a['corresp'] == 'yes':
                                    l_correspondent = True
                            except Exception as noop:
                                pass

                            # get author's name...
                            try:
                                n1 = a.find('string-name')
                                n1.name = 'name'
                            except Exception as noop:
                                pass
                            name = self._name_to_ads(a.find('name').extract())

                            # get named affiliations within the contrib block
                            affs = a.find_all('aff')
                            aff_text = []
                            for i in affs:
                                # special case: some pubs label affils with
                                # <sup>label</sup>, strip them
                                try:
                                    # NOTE: institution-id is actually useful, but at
                                    # at the moment, strip it
                                    a = self._decompose(soup=a, tag='institution-id')
                                    i = self._decompose(soup=i, tag='sup')
                                except Exception as noop:
                                    pass
                                affstr = (i.get_text(separator=' ').strip())
                                (affstr, email_list) = self._fix_affil(affstr)
                                aff_text.append(affstr)
                                i.decompose()

                            # get xrefs...
                            xrefs = a.find_all('xref')
                            xref_aff = []
                            xref_email = []
                            for x in xrefs:
                                try:
                                    if x['ref-type'] == 'aff':
                                        xref_aff.append(x['rid'])
                                    elif x['ref-type'] == 'corresp':
                                        xref_email.append(x['rid'])
                                except Exception as noop:
                                    pass
                                x.decompose()

                            # get orcid
                            contrib_id = a.find_all('contrib-id')
                            orcid = []
                            for c in contrib_id:
                                try:
                                    if c['contrib-id-type'] == 'orcid':
                                        orcid.append(c.get_text(separator=' ').strip())
                                except Exception as noop:
                                    pass
                                c.decompose()

                            # get email(s)...
                            emails = []
                            # first, add any emails found by stripping raw emails out of affil strings above...
                            try:
                                for e in email_list:
                                    emails.append(e)
                            except Exception as noop:
                                pass
                            else:
                                email_list = []
                            try:
                                email = a.find_all('email')
                                for e in email:
                                    try:
                                        emails.append(e.get_text(separator=' ').strip())
                                    except Exception as noop:
                                        pass
                                    e.decompose()
                            except Exception as noop:
                                pass

                            # double-check for other things...
                            extlinks = a.find_all('ext-link')
                            for e in extlinks:
                                # orcid
                                try:
                                    if e['ext-link-type'] == 'orcid':
                                        orcid.append(e.get_text(separator=' ').strip())
                                except Exception as noop:
                                    pass
                                e.decompose()

                        # create the author dict
                        auth.update(corresp=l_correspondent)
                        auth.update(name=name)
                        auth.update(aff=aff_text)
                        auth.update(xaff=xref_aff, xemail=xref_email)
                        auth.update(orcid=orcid)
                        auth.update(email=emails)
                        a.decompose()
                        emails = None
                        orcid = None

                    # this is a list of author dicts
                    self.auth_list.append(auth)
                if self.collab:
                    self.auth_list.append(self.collab)


                # special case: affs defined in contrib-group, but 
                #               not in individual contrib
                contrib_aff = art_contrib_group.find_all('aff')
                for a in contrib_aff:
                    # check and see if the publisher defined an email tag
                    # inside an affil (like IOP does...)
                    nested_email_list = a.find_all('ext-link')
                    if nested_email_list:
                         for e in nested_email_list:
                             key = e['id']
                             value = e.text
                             self.email_xref[key] = value
                             e.decompose()
                    try:
                        key = a['id']
                    except:
                        key = 'ALLAUTH'
                    try:
                        # special case: get rid of <sup>...
                        try:
                            a = self._decompose(soup=a, tag='sup')
                            a = self._decompose(soup=a, tag='institution-id')
                            # getting rid of ext-link eliminates *all* emails,
                            # so this is not the place to fix the iop thing
                            # a = self._decompose(soup=a, tag='ext-link')
                        except Exception as noop:
                            pass
                        affstr = a.get_text(separator=' ').strip()
                        (affstr, email_list) = self._fix_affil(affstr)
                        if email_list:
                            self.email_xref[key] = email_list
                            email_list = []
                        self.xref_dict[key] = affstr
                    except Exception as err:
                        pass


            # now get the xref keys outside of contrib-group:

            # aff xrefs...
            try:
                aff_glob = art_meta.find_all('aff')
            except Exception as noop:
                aff_glob = None
            else:
                try:
                    for a in aff_glob:
                        key = a['id']
                        # special case: get rid of <sup>...
                        try:
                            a = self._decompose(soup=a, tag='sup')
                        except Exception as noop:
                            pass
                        try:
                            # NOTE: institution-id is actually useful, but at
                            # at the moment, strip it
                            a = self._decompose(soup=a, tag='institution-id')
                        except Exception as noop:
                            pass
                        affstr = a.get_text(separator=' ').strip()
                        (affstr, email_list) = self._fix_affil(affstr)
                        self.xref_dict[key] = affstr
                        a.decompose()
                except Exception as err:
                    print('no aff id key!',a)
                    pass

            # author-notes xrefs...
            try:
                authnote_glob = art_meta.find_all('author-notes')
            except Exception as noop:
                authnote_glob = None
            else:
                try:
                    for a in authnote_glob:
                        # emails...
                        cor = a.find_all('corresp')
                        for c in cor:
                            key = c['id']
                            try:
                                c = self._decompose(soup=c, tag='sup')
                            except Exception as noop:
                                pass
                            val = c.get_text(separator=' ').strip()
                            self.xref_dict[key] = val
                            c.decompose()
                except Exception as err:
                    print('no authnote id key!',a)
                    pass

            # finishing up
            self._match_xref()
            self._refield()
            return
        except Exception as err:
            raise JATSContribException(err)
