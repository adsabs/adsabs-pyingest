"""
Utilities for pyingest
"""

import sys
import os.path
import argparse
import importlib
import unidecode

def import_class(name):
    """
    performs the proper imports at runtime and class instantiations;
    for example if name='parsers.zenodo.ZenodoParser', this function
    does the equivalent of calling:
        import parsers.zenodo
        p = parsers.zenodo.ZenodoParser()
        return p
    """
    (mname, cname) = os.path.splitext(name)
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


# This was copied from ADSPipelineUtils because of an upstream dependency
# that doesn't work with python 2.7.  This will be removed once we transition
# to python 3.  [MT, 2020Aug19]

def u2asc(input):
    """
    Converts/transliterates unicode characters to ASCII, using the unidecode package.
    Functionality is similar to the legacy code in adspy.Unicode, but may treat some characters differently
    (e.g. umlauts). Standard unidecode package only handles Latin-based characters.
    :param input: string to be transliterated. Can be either unicode or encoded in utf-8
    :return output: transliterated string, in either unicode or encoded (to match input)
    """

    # TODO If used on anything but author names, add special handling for math symbols and other special chars
    if sys.version_info < (3,):
        test_type = unicode
    else:
        test_type = str
    if not isinstance(input, test_type):
        try:
            input = input.decode('utf-8')
        except UnicodeDecodeError:
            raise Exception('Input must be either unicode or encoded in utf8.')

    try:
        output = unidecode.unidecode(input)
    except UnicodeDecodeError:
        raise Exception('Transliteration failed, check input.')

    if not isinstance(input, test_type):
        output = output.encode('utf-8')

    return output

