import json
from .default import DefaultParser
from .author_names import AuthorNames

class ADSFeedbackParser(DefaultParser):

    def __init__(self,json_string):
        self.data = json.loads(json_string)

    def parse(self,**kwargs):
        output_metadata = dict()

        simple_fields = ['bibcode','abstract','publication','title','authors','comments','keywords','references']

        for field in simple_fields:
            try:
                output_metadata[field] = self.data[field]
            except Exception as err:
                pass

        # Other fields....

        # Pubdate
        try:
           output_metadata['pubdate'] = self.data['publicationDate']
        except Exception as err:
           pass

        # Collection/database:
        try:
            collections = self.data['collection']
            database = list()
            for col in collections:
                if col == 'astronomy':
                    database.append('AST')
                elif col == 'physics':
                    database.append('PHY')
            if database:
                output_metadata['database'] = database
        except Exception as err:
            pass

        # Affiliation and ORCID fields
        try:
            affil_list = self.data['affiliation']
        except Exception as err:
            affil_list = list()
        try:
            orcid_list = self.data['orcid']
        except Exception as err:
            orcid_list = list()

        try:
            n_affil = len(affil_list)
            n_orcid = len(orcid_list)
            n_auth = len(output_metadata['authors'])

            if n_affil == n_auth:
                if n_orcid == n_affil:
                    new_affils = list()
                    for (affil,orcid) in zip(affil_list,orcid_list):
                        newaff = affil + ' <id system="ORCID">' + orcid + '</id>'
                        new_affils.append(newaff)
                    affil_list = new_affils

                output_metadata['affiliations'] = affil_list
            else:
                # send a warning to logger when logging is implemented
                pass
        except Exception as err:
            pass

        # Properties / URLs
        url_types = ['pdf','other','doi','html','arxiv']
        properties = {}
        try:
            url_data = self.data['urls']
            for url in url_data:
                (utype,link) = url.split()
                utype = utype.strip('(').strip(')').upper()
                properties[utype] = link
            if properties:
                output_metadata['properties'] = properties
        except Exception as err:
            pass

        # Fix names
        old_names = output_metadata['authors']
        authparse = AuthorNames()
        new_names = [authparse.parse(name) for name in old_names]
        output_metadata['authors'] = new_names

        return output_metadata
