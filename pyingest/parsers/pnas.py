import requests
from pyingest.config import config
from pyingest.parsers.default import BaseBeautifulSoupParser
from pyingest.parsers.author_names import AuthorNames
from pyingest.parsers.affils import AffiliationParser


class URLError(Exception):
    pass


class ContentError(Exception):
    pass


class NotPUblishedError(Exception):
    pass


class PNASParser(BaseBeautifulSoupParser):

    def __init__(self):
        pass

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
        except Exception, err:
            print "title not found:",err


        # Abstract
        try:
            abstract_meta = data.find_all(attrs={'name':'citation_abstract'})
            for a in abstract_meta:
                try:
                    a['scheme']
                except Exception, err:
                    output_metadata['abstract'] = a['content'].lstrip('<p>').rstrip('</p>')
        except Exception, err:
            print "abstract not found:",err
            pass


        # Authors
        try:
            author_meta = data.find_all(attrs={'name':'citation_author'})
            for a in author_meta:
                auth_list.append(a['content'])
        except Exception, err:
            print "problem with authors",err

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
        except Exception, err:
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
        except Exception, err:
            pass

        # Keywords
        try:
            keys = data.findAll('li', {'class':'kwd'})
            output_metadata['keywords'] = ', '.join(k.text for k in keys)
        except Exception, err:
            print "LOL ERR:",err
            pass

        # Affiliations/ORCID/email addresses:
        n_authors = len(auth_list)
        affil_list = []
        for i in range(0,n_authors):
            class_attr = 'author-tooltip-' + str(i)
            affils = []
            try:
                div_data = data.find('div', {"class":class_attr})
            except Exception, err:
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
        except Exception, err:
            output_metadata['authors'] = "; ".join(auth_list)
        try:
            parse_affil = AffilationParser()
            affil_new = [parse_affil.parse(aff) for aff in affil_list]
            output_metadata['affiliations'] = affil_new
        except Exception, err:
            output_metadata['affiliations'] = affil_list

        return output_metadata
