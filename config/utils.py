"""
Utilities for pyingest
"""

import os.path
import argparse
import importlib

def import_class(name):
    """                                                                                                                          
    performs the proper imports at runtime and class instantiations;                                                             
    for example if name='parsers.zenodo.ZenodoParser', this function                                                             
    does the equivalent of calling:                                                                                              
        import parsers.zenodo                                                                                                    
        p = parsers.zenodo.ZenodoParser()                                                                                        
        return p                                                                                                                 
    """
    (mname,cname) = os.path.splitext(name)
    if cname:
        cname = cname.strip('.')
    module = importlib.import_module(mname)
    return module.__getattribute__(cname)()


def parse_arguments():
    """                                                                                                                          
    returns an argparse.ArgumentParser().parse_args() object                                                                     
    """
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '--debug',
        default=False,
        action='count',
        dest='debug',
        help='turn on debugging'
        )
    argp.add_argument(
        '--parser',
        type=str,
        default='parsers.default.DefaultParser',
        dest='parser',
        help='specify parser class to use'
        )
    argp.add_argument(
        '--validator',
        type=str,
        default='validators.ads.SimpleValidator',
        dest='validator',
        help='specify validator class to use'
        )
    argp.add_argument(
        '--serializer',
        type=str,
        default='serializers.classic.Tagged',
        dest='serializer',
        help='specify serializer class to use'
        )
    argp.add_argument('files', nargs='+')
    return argp.parse_args()

