import re
import copy
import json

infile = 'pyingest/config/html5.txt'
ent_dict = dict()
with open(infile,'rU') as fent:
    for l in fent.readlines():
        carr = l.rstrip().split('\t')
        
        uni_entity = carr[0]
        name_entity = carr[1]
        hex_entity = carr[2]
        dec_entity = carr[3]

        for c in name_entity.split():
            ent_dict[c] = dec_entity
        # for c in uni_entity.split():
            # ent_dict[c] = dec_entity
        # redefine some ADS-specific translations

    ent_dict["&rsquo;"] = '\''
    ent_dict["&lsquo;"] = '\''
    ent_dict["&nbsp;"] = ' '
    ent_dict["&mdash;"] = '-'
    ent_dict["&ndash;"] = '-'
    ent_dict["&rdquo;"] = '\"'
    ent_dict["&ldquo;"] = '\"'
    ent_dict["&minus;"] = '-'
    ent_dict["&plus;"] = '+'
    ent_dict["&thinsp;"] = ' '
        


class EntityConverter():

    def __init__(self):
        self.input_text = ''
        self.output_text = ''
        self.ent_dict = ent_dict

    def convert(self):
        o = self.input_text
        for k, v in self.ent_dict.items():
            ox = copy.deepcopy(o)
            o = re.sub(k, v, ox)
        self.output_text = o


