import html
from adsputils import u2asc

class BadAuthorInitialException(Exception):
    pass


class AuthorInitial(object):

     def __init__(self):
         pass

     def get_author_init(self, namestring):
         try:
             instring = html.unescape(namestring)
             outstring = u2asc(instring)[0]
             if outstring.isalpha():
                 return outstring.upper()
         except Exception as err:
             raise BadAuthorInitialException(err)
         else:
             return '.'
