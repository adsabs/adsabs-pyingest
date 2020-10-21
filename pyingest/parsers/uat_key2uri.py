from builtins import object
import re
import sys
from collections import OrderedDict
from pyingest.config import config


class UATURIConverter(object):
    '''
    Takes a string containing a comma-separated list of string as input,
    and converts any that match UAT entities to their UAT:URI_# instead 
    (not including URL).  Returns a string consisting of comma-separated
    keywords/uris.
    '''

    def convert_to_uri(self,kw_list):
        try:
            kw_list_new = [x.strip() for x in kw_list.split(',')]
            if sys.version_info > (3,):
                kw_list_new = list(dict.fromkeys(kw_list_new))
            else:
                kw_list_new = list(OrderedDict.fromkeys(kw_list_new))
            uat_conv = UATURIConverter()
            kwl = list()
            for kw in kw_list_new:
                if kw.lower() in config.UAT_ASTRO_URI_DICT.keys():
                    kout = 'UAT:' + config.UAT_ASTRO_URI_DICT[kw.lower()]
                else:
                    kout = kw
                kwl.append(kout)
            return ', '.join(kwl)
        except Exception as err:
            return kw_list
