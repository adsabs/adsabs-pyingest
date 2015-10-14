import os
import sys
import json
import jsonschema

SIMPLE_SCHEMA = os.path.join(os.path.dirname(__file__), 'simple.schema.json')
ZENODO_SCHEMA = os.path.join(os.path.dirname(__file__), 'zenodo.schema.json')
NULL_SCHEMA = os.path.join(os.path.dirname(__file__), 'null.schema.json')

SCHEMA_VALIDATOR = jsonschema.validators.Draft4Validator

class Validator(object):

    def __init__(self, file):
        self.schema_file = file
        self.schema = self._get_schema(file)
        self.validator = SCHEMA_VALIDATOR(self.schema)

    def _get_schema(self, file):
        with open(file, 'r') as fp:
            s = json.load(fp)
        return s

    def validate(self, document):
        """
        Validates the dodcument.  
        Right now all we do is check the "simple" schema above.
        TODO: we should deal with proper encoding of the
        HTML entities allowed in ADS metadata fields.
        Check out https://github.com/jsocol/bleach
        """
        self.validator.validate(document)

class NullValidator(Validator):
    def __init__(self):
        super(self.__class__, self).__init__(NULL_SCHEMA)

class SimpleValidator(Validator):
    def __init__(self):
        super(self.__class__, self).__init__(SIMPLE_SCHEMA)

class ZenodoValidator(Validator):
    def __init__(self):
        super(self.__class__, self).__init__(ZENODO_SCHEMA)
