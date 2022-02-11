from .default import BaseBeautifulSoupParser
from .author_names import AuthorNames

class XmlLoadException(Exception):
    pass

class NoSoupForYouException(Exception):
    pass


class TooManyDocumentsException(Exception):
    pass


class NotCrossrefXMLException(Exception):
    pass


class CrossrefXMLParser(BaseBeautifulSoupParser):

    def __init__(self):
        pass


    def _get_dict(self, data, parser='lxml-xml'):
        try:
            soup = self.bsstrtodict(data, parser)
            records_in_file = soup.find_all('doi_record')
            if len(records_in_file) > 1:
                raise TooManyDocumentsException('This file has %s records, should have only one!' % len(records_in_file))
        except Exception as err:
            raise XmlLoadException(err)
        else:
            return records_in_file[0]


    def parse(self, data, **kwargs):
        output_metadata = {}
        try:
            record = self._get_dict(data)
        except Exception as err:
            raise NoSoupForYouException(err)
        else:
            try:
                metadata = record.find('crossref').extract()
            except Exception as err:
                raise NotCrossrefXMLException(err)
            else:

                # book data
                book = metadata.find('book').extract()
                if book:
                    chapter = book.find('content_item', component_type='chapter').extract()

                # All the following from chapter

                # Title
                if chapter.titles.title:
                    output_metadata['title']=str(chapter.titles.title.extract().string)

                if chapter.contributors:
                    auth_list = []
                    a = AuthorNames()
                    contribs = chapter.contributors.extract()
                    for auth in contribs.find_all('person_name', contributor_role='author'):
                        au = a.parse(', '.join([str(auth.surname.extract().string), str(auth.given_name.extract().string)]))
                        auth_list.append(au)
                    output_metadata['authors'] = ('; '.join(auth_list))

                # References
                ref_list_text = []
                try:
                    refs_soup = chapter.find('citation_list').extract()
                    refs = refs_soup.find_all('citation') 
                    for r in refs:
                        ref_list_text.append(str(r.extract()))
                except Exception as err:
                    pass
                # output_metadata['refhandler_list']=ref_list_text

                print(chapter)

                


               




        return output_metadata
      
               




















