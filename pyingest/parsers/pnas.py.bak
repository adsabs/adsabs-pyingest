import requests
from pyingest.config.utils import u2asc
from pyingest.config import config
from pyingest.parsers.default import BaseBeautifulSoupParser
from pyingest.parsers.author_names import AuthorNames
from pyingest.parsers.affils import AffiliationParser
from pyingest.parsers.uat_key2uri import UATURIConverter


class URLError(Exception):
    pass


class ContentError(Exception):
    pass


class NotPUblishedError(Exception):
    pass


class PNASParser(BaseBeautifulSoupParser):

    def __init__(self):
        pass

    def get_author_init(self, namestring):
        output = u2asc(namestring)
        for c in output:
            if c.isalpha():
                return c.upper()
        return u'.'

    def get_buffer(self, url, **kwargs):
        hostname = url.split('/')[2]
        if hostname != 'www.pnas.org':
            raise URLError("This parser is only for PNAS.org RSS feed")
        try:
            pnas_buffer = requests.get(url)
        except IOError:
            raise URLError("Could not open %s" % url)
        return pnas_buffer

    def resource_dict(self, fp, **kwargs):
        d = self.bsstrtodict(fp, **kwargs)
        return d

    def parse(self, url, **kwargs):

        data = self.resource_dict(self.get_buffer(url).text)

        output_metadata = {}

        meta_data = data.find_all('meta')

        auth_list = []


        # Title
        try:
            title_meta = data.find_all(attrs={'name':'citation_title'})
            for t in title_meta:
                if t['content']:
                    output_metadata['title'] = t['content']
        except Exception as err:
            # print "title not found:",err
            pass


        # Abstract
        try:
            abstract_meta = data.find_all(attrs={'name':'citation_abstract'})
            for a in abstract_meta:
                try:
                    a['scheme']
                except Exception as err:
                    output_metadata['abstract'] = a['content'].lstrip('<p>').rstrip('</p>')
        except Exception as err:
            # print "abstract not found:",err
            pass


        # Authors
        try:
            author_meta = data.find_all(attrs={'name':'citation_author'})
            for a in author_meta:
                auth_list.append(a['content'])
        except Exception as err:
            # print "problem with authors",err
            pass

        # Volume, issue, first/last page for 'publication'
        try:
            vol = data.find_all(attrs={'name':'citation_volume'})[0]['content']
            iss = data.find_all(attrs={'name':'citation_issue'})[0]['content']
            fpg = data.find_all(attrs={'name':'citation_firstpage'})[0]['content']
            lpg = data.find_all(attrs={'name':'citation_lastpage'})[0]['content']
            volume = vol + ', issue ' + iss
            page = fpg + '-' + lpg
            journal_string = "Proceedings of the National Academy of Sciences, vol. %s, pp. %s"
            output_metadata['publication'] = journal_string % (volume,page)
            output_metadata['volume'] = vol
        except Exception as err:
            pass

        # Properties (DOI, etc)
        output_metadata['properties'] = dict()
        try:
            doi = data.find_all(attrs={'name':'citation_doi'})[0]['content']
        except:
            pass
        else:
            output_metadata['properties']['DOI'] = doi
        try:
            htm = data.find_all(attrs={'name':'citation_full_html_url'})[0]['content']
        except:
            pass
        else:
            output_metadata['properties']['HTML'] = htm
        try:
            pdf = data.find_all(attrs={'name':'citation_pdf_url'})[0]['content']
        except:
            pass
        else:
            output_metadata['properties']['PDF'] = pdf

        # Database
        output_metadata['database'] = 'PHY'
        try:
            db_strings = data.findAll('li', {'class':'last even'})
            for db_s in db_strings:
                if db_s.a.get_text() == 'Astronomy':
                    output_metadata['database'] = 'AST'
        except Exception as err:
            pass

        # Keywords
        try:
            keys = data.findAll('li', {'class':'kwd'})
            keystrings = ', '.join(k.text for k in keys)
            uat_cnv = UATURIConverter()
            output_metadata['keywords'] = uat_cnv.convert_to_uri(keystrings)
        except Exception as err:
            pass
        

        # Pubdate
        try:
            pubdate = data.findAll('meta', {'name':'citation_publication_date'})[0]['content']
            ymd = pubdate.split('/')
            output_metadata['pubdate'] = ymd[1].rjust(2,'0')+ '/' + ymd[0]
        except Exception as err:
            pass

        # Affiliations/ORCID/email addresses:
        n_authors = len(auth_list)
        affil_list = []
        for i in range(0,n_authors):
            class_attr = 'author-tooltip-' + str(i)
            affils = []
            try:
                div_data = data.find('div', {"class":class_attr})
            except Exception as err:
                pass
            else:
                if div_data:
                    # name = div_data.find('div', {'class':'author-tooltip-name'}).contents
                    affl = div_data.findAll('div', {'class':'author-affiliation'})
                    for a in affl:
                        a.find('span', {'class':'nlm-sup'}).decompose()
                        affils.append(a.get_text().rstrip(';'))

                    orcid = div_data.find('li', {'class':'author-orcid-link'})
                    if orcid:
                        affils.append('<id system="orcid">'+orcid.a['href'].split('/')[-1]+'</id>')

                    email = div_data.find('li', {'class':'author-corresp-email-link last'})
                    if email:
                        affils.append('<email>'+email.a.get_text()+'</email>')


            affil_list.append('; '.join(affils))
       
        # process both the author name and affiliation data
        try:
            parse_names = AuthorNames()
            output_metadata['authors'] = parse_names.parse("; ".join(auth_list))
        except Exception as err:
            output_metadata['authors'] = "; ".join(auth_list)
        try:
            parse_affil = AffilationParser()
            affil_new = [parse_affil.parse(aff) for aff in affil_list]
            output_metadata['affiliations'] = affil_new
        except Exception as err:
            output_metadata['affiliations'] = affil_list

        # Now you can make the bibcode...
        year = str(int(vol) + 1903)
        bibstem = 'PNAS.'
        vol_bib = vol.rjust(4,'.')
        fpg_bib = fpg.rjust(5,'.')
        auth_init = self.get_author_init(output_metadata['authors'][0])
        output_metadata['bibcode'] = year + bibstem + vol_bib + fpg_bib + auth_init

        # References
        try:
            reflist = data.findAll('meta', {'name':'citation_reference'})
            output_metadata['refhandler_list'] = []
            for r in reflist:
                output_metadata['refhandler_list'].append(r)
        except Exception as err:
            # print "in pnas references:",err
            pass
        

        return output_metadata
