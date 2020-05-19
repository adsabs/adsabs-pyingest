### parser for arXiv records in Dublin Core XML format ###

from xml.parsers import expat
from adsputils import u2asc
from pyingest.parsers.dubcore import DublinCoreParser
from pyingest.parsers.author_names import AuthorNames


class MissingAuthorException(Exception):
    pass


class MissingTitleException(Exception):
    pass


class MissingAbstractException(Exception):
    pass


class MissingIDException(Exception):
    pass


class MissingDateException(Exception):
    pass


class EmptyParserException(Exception):
    pass


class ArxivParser(DublinCoreParser):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.author_names = AuthorNames()
        self.author_collaborations_params = {
            'keywords': ['group', 'team', 'collaboration'],
            'first_author_delimiter': ':',
            'remove_the': False,
            'fix_arXiv_mixed_collaboration_string': True,
        }

    def get_author_init(self, namestring):
        output = u2asc(namestring)
        for _c in output:
            if _c.isalpha():
                return _c.upper()
        return u'.'

    def parse(self, fp, **kwargs):


        try:
            result = super(self.__class__, self).parse(fp, **kwargs)
        except expat.ExpatError:
            raise EmptyParserException("Not parseable xml")
        else:
            pass

        if result['abstract']:
            result['comments'] = [x.replace('Comment:', '').strip() for x in result['abstract'][1:]]
            result['abstract'] = result['abstract'][0]

        if result['authors']:
            result['authors'] = self.author_names.parse(result['authors'], collaborations_params=self.author_collaborations_params)

        if result['bibcode']:
            idarray = result['bibcode'].split(':')
            arxiv_id = idarray[-1]

            result['publication'] = 'eprint arXiv:' + arxiv_id

            if arxiv_id[0].isalpha():
                arx_field = arxiv_id.split('/')[0].replace('-', '.')
                arx_num = arxiv_id.split('/')[1]
                arx_yy = arx_num[0:2]
                if arx_num[2] == '0':
                    arx_num = arx_num[3:]
                else:
                    arx_num = arx_num[2:]
            else:
                arx_field = 'arXiv'
                arx_num = arxiv_id.replace('.', '')
                n_1 = arx_num[0:4]
                n_2 = arx_num[4:]
                if len(n_2) < 5:
                    arx_num = n_1 + u'.' + n_2
                else:
                    arx_num = n_1 + n_2
                arx_yy = arx_num[0:2]

            if int(arx_yy) > 90:
                year = u'19' + arx_yy
            else:
                year = u'20' + arx_yy

            author_init = self.get_author_init(result['authors'])

            bibcode1 = year + arx_field
            bibcode2 = arx_num + author_init
            if len(bibcode1) + len(bibcode2) < 19:
                bibcodex = u'.' * (19 - len(bibcode1) - len(bibcode2))
                bibcode = bibcode1 + bibcodex + bibcode2
            else:
                bibcode = bibcode1 + bibcode2
            result['bibcode'] = bibcode

        if result['properties']:
            prop = {}
            pubnote_prop = []
            for _x in result['properties']:
                if 'http://arxiv.org' in _x or 'https://arxiv.org' in _x:
                    prop['HTML'] = _x
                else:
                    if 'doi:' in _x:
                        prop['DOI'] = _x
                    pubnote_prop.append(_x)
            result['properties'] = prop

            if result['comments']:
                if pubnote_prop:
                    result['comments'] = result['comments'] + pubnote_prop

        return result
