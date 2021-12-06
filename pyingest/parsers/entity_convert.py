import os
import re
from namedentities import named_entities

from adsputils import load_config

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__),'../../'))
conf = load_config(proj_home=proj_home)

re_ents = re.compile(r'&[a-z0-9]+;|&#[0-9]{1,6};|&#x[0-9a-fA-F]{1,6};')


class EntityConverter(object):

    def __init__(self):
        self.input_text = ''
        self.output_text = ''
        self.ent_dict = conf.get('ENTITY_DICTIONARY', {})

    def convert(self):
        o = named_entities(self.input_text)
        oents = list(dict.fromkeys(re.findall(re_ents,o)))
        
        for e in oents:
            try:
                enew = self.ent_dict[e]
            except:
                pass
            else:
                o = re.sub(e, enew, o)
        self.output_text = o
