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
            surname = name.find('surname').contents[0]
            given = name.find('given-names').contents[0]
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
                    # if you found any emails in an affstring, add them to email field
                    if item in self.email_xref:
                        a['email'].extend(self.email_xref[item])
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
            esplit = em.strip().split()
            for e in esplit:
                if '@' in e:
                    email_new.append(e.strip())
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
            xxx = self.regex_email.match(a.strip())
            if self.regex_email.match(a.strip()):
                emails.append(a.strip())
            else:
                new_aff.append(a.strip())
        newaffstr = '; '.join(new_aff)
        return (newaffstr, emails)
            


    def _refield(self):
        out_auth = []
        out_aff = []
        for a in self.auth_list:
            name = a['name']
            aff = a['aff']
            email = self._fix_email(a['email'])
            orcid = self._fix_orcid(a['orcid'])
            aff_new = '; '.join(aff)
            if orcid:
                orcid = '; '.join(orcid).strip()
                orcid = '; <id system="orcid">' + orcid + '</id>'
                aff_new = aff_new + orcid
            if email:
                email = '; '.join(email).strip()
                email = '<email>' + email + '</email>'
                aff_new = aff_new + ' ' + email
            aff_new = self.regex_spcom.sub(',',aff_new)
            aff_new = self.regex_multisp.sub(' ',aff_new)
            out_auth.append(name)
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
                #art_meta.label.decompose()
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
                    if a['contrib-type'] == 'collab' or 'collab' in a.text:
                        # print('ZOMG COLLAB: %s' % a)
                        # print('ZOMG COLLAB!', a)
                        # c.decompose()
                        pass
                    # print('lol auth:',auth)
                    elif a['contrib-type'] == 'author':
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
                            emails.extend(email_list)
                        except Exception as noop:
                            pass
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

                    # this is a list of author dicts
                    self.auth_list.append(auth)


                # special case: affs defined in contrib-group, but 
                #               not in individual contrib
                contrib_aff = art_contrib_group.find_all('aff')
                for a in contrib_aff:
                    try:
                        key = a['id']
                    except:
                        key = 'ALLAUTH'
                    try:
                        # special case: get rid of <sup>...
                        try:
                            a = self._decompose(soup=a, tag='sup')
                            a = self._decompose(soup=a, tag='institution-id')
                        except Exception as noop:
                            pass
                        affstr = a.get_text(separator=' ').strip()
                        (affstr, email_list) = self._fix_affil(affstr)
                        if email_list:
                            self.email_xref[key] = email_list
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
                            # a.sup.decompose()
                        except Exception as noop:
                            pass
                        try:
                            # NOTE: institution-id is actually useful, but at
                            # at the moment, strip it
                            a = self._decompose(soup=a, tag='institution-id')
                            # a.institution-id.decompose()
                        except Exception as noop:
                            pass
                        affstr = a.get_text(separator=' ').strip()
                        (affstr, email_list) = self._fix_affil(affstr)
                        # self.xref_dict[key] = a.get_text(separator=' ').strip()
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
                                # c.sup.decompose()
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


def main():

    import html
    from glob import glob
    from bs4 import BeautifulSoup

    files = glob('*.xml')
    for f in files:

        print('\n%s' % f)
        with open(f,'rb') as fx:
            data = fx.read()

        # Cheat: beautifulsoup is expecting xml with the 'lxml-xml' parser,
        #        so HTML entities will get cut without the following:
        data = html.unescape(data.decode('utf-8'))

        '''
        WARNING: bs4 seems to choke on HTML comments, so if you use lxml-xml
        on (at least) Taylor & Francis, it will fail....
        
        soup = BeautifulSoup(data,'lxml-xml')
        if 't-f_ex' in f:
            print('data: "%s"' % data)
            print('soup: "%s"' % soup)
        '''
        soup = BeautifulSoup(data,'lxml')
        article_meta = soup.find('article-meta')
        try:
            test = JATSContribs(soup=article_meta)
            test.parse()
            foo = test.output
            print(foo)
        except Exception as err:
            print('it didnt work: %s' % err)
    return


if __name__ == '__main__':
    main()