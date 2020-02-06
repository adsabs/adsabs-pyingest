import re
import copy
import json
import namedentities

infile = 'pyingest/config/html5.txt'
ent_dict = dict()
with open(infile,'rU') as fent:
    for l in fent.readlines():
        carr = l.rstrip().split('\t')
        
        uni_entity = None
        name_entity = None
        hex_entity = None
        dec_entity = None
        if len(carr) >= 4:
            uni_entity = carr[0]
            name_entity = carr[1]
            hex_entity = carr[2]
            dec_entity = carr[3]
        else:
            print "broken HTML entity:",l.rstrip()
            name_entity = "xxxxx"
            uni_entity = "xxxxx"
            dec_entity = "xxxxx"

        for c in name_entity.split():
            try:
                ent_dict[c] = dec_entity
            except Exception, err:
                print "Error splitting name_entity: '%s'" % name_entity

    # ADS-specific translations
    # have been added to html5.txt
    ent_dict['&rsquo;'] = '\''
    ent_dict['&lsquo;'] = '\''
    ent_dict['&nbsp;'] = ' '
    ent_dict['&mdash;'] = '-'
    ent_dict['&ndash;'] = '-'
    ent_dict['&rdquo;'] = '\"'
    ent_dict['&ldquo;'] = '\"'
    ent_dict['&minus;'] = '-'
    ent_dict['&plus;'] = '+'
    ent_dict['&thinsp;'] = ' '
    ent_dict['&hairsp;'] = ' '
    ent_dict['&ensp;'] = ' '
    ent_dict['&emsp;'] = ' '
        
class EntityConverter():

    def __init__(self):
        self.input_text = ''
        self.output_text = ''
        self.ent_dict = ent_dict

    def convert(self):
        o = self.input_text
        ox = copy.deepcopy(namedentities.named_entities(o))
        for k, v in self.ent_dict.items():
            ox = re.sub(k, v, ox)
        self.output_text = ox


