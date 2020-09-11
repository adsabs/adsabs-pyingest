from builtins import object
import re
from pyingest.config import config


class EntityConverter(object):

    def __init__(self):
        self.input_text = ''
        self.output_text = ''
        self.ent_dict = config.ENTITY_DICTIONARY

    def convert(self):
        o = self.input_text
        # ox = o
        for k, v in list(self.ent_dict.items()):
            # ox = re.sub(k, v, ox)
            o = re.sub(k, v, o)
        self.output_text = o
