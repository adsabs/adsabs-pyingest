import sys

class MissingParser(Exception):
    pass

class DefaultParser(object):
    raise MissingParser("No parser defined")
