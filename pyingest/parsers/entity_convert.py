import re
from pyingest.config import config

class EntityConverter():

    def __init__(self):
        self.input_text = ''
        self.output_text = ''
        self.ent_dict = config.ENTITY_DICTIONARY

    def convert(self):
        o = self.input_text
        ox = o
        for k, v in self.ent_dict.items():
            ox = re.sub(k, v, ox)
        self.output_text = ox


