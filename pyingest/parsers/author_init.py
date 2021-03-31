import namedentities
from pyingest.config.utils import u2asc

class BadAuthorInitialException(Exception):
    pass


class AuthorInitial(object):

     def __init__(self):
         pass

     def get_author_init(self, namestring):
         try:
             instring = namedentities.unicode_entities(namestring)
             outstring = u2asc(instring)[0]
             if outstring.isalpha():
                 return outstring
         except Exception as err:
             raise BadAuthorInitialException(err)
         else:
             return '.'
