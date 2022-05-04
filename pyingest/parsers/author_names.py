from past.builtins import basestring
import os
import sys
import re
import logging
from adsputils import u2asc
from pyingest.config import config
from namedentities import named_entities, unicode_entities
import nameparser


class AuthorNames(object):
    """
    Author names parser
    """

    def _read_datfile(self, filename):
        output_list = []
        if sys.version_info > (3,):
            open_mode = 'r'
        else:
            open_mode = 'rU'
        try:
            fp = open(filename, open_mode)
        except Exception as err:
            logging.exception("Error reading file: %s", filename)
        else:
            with fp:
                for l in fp.readlines():
                    if l.strip() != '' and l[0] != '#':
                        output_list.append(l.strip())
        return output_list

    def _normalize(self, authors_str, delimiter=u';', collaborations_params={}):
        """
        Normalizes a string of author name separated by some delimiter
        """
        default_collaborations_params = self.default_collaborations_params.copy()
        default_collaborations_params.update(collaborations_params)
        collaborations_params = default_collaborations_params
        normalized_authors_list = []
        
        for author_str in authors_str.split(delimiter):
            normalized_authors_list.append(self._normalize_author(author_str, collaborations_params))
        return (delimiter + u' ').join(normalized_authors_list)

    def _normalize_author(self, author_str, collaborations_params):
        """
        Normalizes an author name string ensuring capitalization and
        transforming first name to only initials
        """
        try:
            # Transliterates unicode characters to ASCII
            author_str = u2asc(author_str.strip())
        except Exception as err:
            logging.exception("Unexpected error transliterating author name\
                               unicode string to ASCII")
            # TODO: Implement better error control
            return self._normalize_author(self.unknown_author_str,
                                          collaborations_params)

        # Check first if it is a collaboration, given that collaboration strings
        # may have commas and it may be wrongly interpreted as a name
        collaboration = False
        for keyword in collaborations_params['keywords']:
            if keyword in author_str.lower():
                collaboration = True
                break
        if collaboration:
            # Make sure there are no commas to avoid interpreting this name as 'last, first name'
            normalized_author_str = author_str.replace(",", "")
        else:
            match = self.regex_author.search(author_str)
            if match:
                # Last name detected
                ## Using .title() breaks dutch last names!
                # last_name = match.group('last_name').strip().title()
                last_name = match.group('last_name').strip()
                initials_list = []
                # Collect initials from first name if it is present
                for i in range(self.max_first_name_initials):
                    key = 'initial' + str(i)
                    if match.group(key):
                        initials_list.append(match.group(key).strip().upper())
                #initials_list.remove(".")
                initials_str = u" ".join(initials_list)
                # Form normalized author string where capitalization is guaranteed
                normalized_author_str = "{}, {}".format(last_name, initials_str)
                # Make sure there are no dots
                normalized_author_str = normalized_author_str.replace(u".", u"")
            else:
                # Make sure there are no commas to avoid interpreting this
                # name as 'last, first name'
                normalized_author_str = author_str.replace(u",", u"")
                # Make sure there are no dots or commas
                normalized_author_str = normalized_author_str.replace(u".", u"")

        normalized_author_str = normalized_author_str.strip()
        if len(normalized_author_str) == 0:
            normalized_author_str = self.normalized_unknown_author_str
        return normalized_author_str

    def __init__(self, data_dirname=config.AUTHOR_ALIAS_DIR,
                 unknown_author_str=u'',
                 max_first_name_initials=6):
        self.max_first_name_initials = max(1, max_first_name_initials)
        self.normalized_unknown_author_str = u''
        self.dutch_last_names = [u"van", u"von", u"'t", u"den", u"der", u"van't"]

        # Paths
        if not os.path.isdir(data_dirname):
            data_dirname = os.path.join(os.path.dirname(os.path.realpath(
                __file__)), "../tests/data/authors/")
        logging.info("Loading ADS author names from: %s", data_dirname)
        self.first_names = self._read_datfile(os.path.join(data_dirname,
                                              'first.dat'))
        self.last_names = self._read_datfile(os.path.join(data_dirname,
                                             'last.dat'))
        prefix_names = self._read_datfile(os.path.join(data_dirname,
                                          'prefixes.dat'))
        suffix_names = self._read_datfile(os.path.join(data_dirname,
                                          'suffixes.dat'))

        # TODO: Change data files, do not hard-code changes here
        self.first_names.append('Md')
        self.last_names.append('Y')

        try:
            for s in prefix_names:
                nameparser.config.CONSTANTS.titles.add(s)
            for s in suffix_names:
                nameparser.config.CONSTANTS.suffix_acronyms.add(s)
                nameparser.config.CONSTANTS.suffix_not_acronyms.add(s)
        except Exception as e:
            logging.exception("Unexpected error setting up the nameparser")
            raise BaseException(e)

        # Setup the nameparser package and remove *all* of the preset titles:
        nameparser.config.CONSTANTS.titles.remove(*nameparser.config.CONSTANTS.titles)
        nameparser.config.CONSTANTS.suffix_acronyms.remove(*nameparser.config.CONSTANTS.suffix_acronyms)
        nameparser.config.CONSTANTS.suffix_not_acronyms.remove(*nameparser.config.CONSTANTS.suffix_not_acronyms)
        nameparser.config.CONSTANTS.string_format = u'{last}, {first} "{nickname}", {suffix}, {title}'

        # Compile regular expressions
        self.regex_initial = re.compile(r"\. *(?!,)")
        self.regex_etal = re.compile(r",? et ?al\.?")
        self.regex_and = re.compile(r" and ")
        self.regex_dash = re.compile(r"^-")
        self.regex_quote = re.compile(r"^'")
        self.regex_the = re.compile(r"^[Tt]he ")
        self.regex_author = re.compile(r"^(?P<last_name>[^,]+),\s*(?P<initial0>\w)\S*" + "".join([r"(?:\s*(?P<initial{}>\w)\S*)?".format(i + 1) for i in range(self.max_first_name_initials - 1)]))

        # Default collaboration parameters
        self.default_collaborations_params = {
            'keywords': ['group', 'team', 'collaboration', 'consortium'],
            'first_author_delimiter': ':',
            'remove_the': True,
            'fix_arXiv_mixed_collaboration_string': False,
        }

        # Default unknown author
        self.unknown_author_str = unknown_author_str
        self.normalized_unknown_author_str = self._normalize(self.unknown_author_str)

    def _extract_collaboration(self, collaboration_str, default_to_last_name, delimiter, collaborations_params):
        """
        Verifies if the author name string contains a collaboration string
        The collaboration extraction can be controlled by the dictionary
        'collaborations_params'.
        """
        corrected_collaboration_str = u''  # Default
        try:
            for keyword in collaborations_params['keywords']:
                if keyword in collaboration_str.lower():
                    collaboration_str = re.sub(keyword, keyword.capitalize(), collaboration_str)
                    if collaborations_params['remove_the']:
                        corrected_collaboration_str = self.regex_the.sub(u'', collaboration_str)
                    else:
                        corrected_collaboration_str = collaboration_str

                    if collaborations_params['fix_arXiv_mixed_collaboration_string']:
                        # TODO: Think a better way to account for this
                        # specific cases if there's a ',' in the string,
                        # it probably includes the 1st author
                        string_list = corrected_collaboration_str.split(',')
                        if len(string_list) == 2:
                            # Based on an arXiv author case: "collaboration,
                            # Gaia"
                            string_list.reverse()
                            corrected_collaboration_str = u' '.join(string_list)

                    if collaborations_params['first_author_delimiter']:
                        # Based on an arXiv author case: "<tag>Collaboration:
                        # Name, Author</tag>"
                        authors_list = corrected_collaboration_str.split(collaborations_params['first_author_delimiter'])
                        corrected_authors_list = []
                        for author in authors_list:
                            if keyword in author.lower():
                                corrected_authors_list.append(author.strip())
                            else:
                                corrected_authors_list.append(self._reorder_author_name(author.strip(), default_to_last_name))
                        corrected_collaboration_str = (delimiter + u' ').join(corrected_authors_list).strip()
                    break
        except Exception as e:
            logging.exception("Unexpected error in collaboration checks")
        is_collaboration_str = corrected_collaboration_str != u''
        return is_collaboration_str, corrected_collaboration_str

    def _clean_author_name(self, author_str):
        """
        Remove useless characters in author name string
        """
        author_str = self.regex_initial.sub('. ', author_str)
        author_str = self.regex_etal.sub('', author_str)
        author_str = self.regex_and.sub(' ', author_str)
        author_str = author_str.replace(' .', '.').replace('  ', ' ').replace(' ,', ',')
        author_str = author_str.strip()
        return author_str

    def _reorder_author_name(self, author_str, default_to_last_name):
        """
        Automatically detect first and last names in an author name string and reorder
        using the format: last name, first name
        """
        author = nameparser.HumanName(author_str)
        if author.first == u'Jr.' and author.suffix != '':
            author.first = author.suffix
            author.suffix = u'Jr.'

        if author.middle:
            # Move middle names to first name if detected as so,
            # or move to last name if detected as so
            # or move to the default
            add_to_first = []
            add_to_last = []
            last_name_found = False

            middle_name_list = author.middle.split()

            try:
                for middle_name in middle_name_list:
                    middle_name_length = len(unicode_entities(middle_name).strip('.').strip('-'))  # Ignore '.' or '-' at the beginning/end of the string
                    middle_name_upper = middle_name.upper()
                    if (middle_name_length <= 2 and middle_name_upper not in self.last_names and "'" not in middle_name) \
                        or (middle_name_upper in self.first_names and middle_name_upper not in self.last_names) \
                        or (self.regex_dash.sub('', middle_name_upper) in self.first_names and self.regex_dash.sub('', middle_name_upper) not in self.last_names) \
                        or (self.regex_quote.sub('', middle_name_upper) in
                            self.first_names and self.regex_quote.sub('',
                            middle_name_upper) not in self.last_names):
                        # Case: First name found
                        # Middle name is found in the first names ADS
                        # list and not in the last names ADS list
                        if last_name_found:
                            # Move all previously detected first names to
                            # last name since we are in a situation where
                            # we detected:
                            # F F L F
                            # hence we correct it to:
                            # L L L F
                            # where F is first name and L is last name
                            add_to_first += add_to_last
                            add_to_last = []
                            last_name_found = False
                        add_to_first.append(middle_name)
                    elif last_name_found or middle_name.upper() in self.last_names:
                        # Case: Last name found
                        add_to_last.append(middle_name)
                        last_name_found = True
                    else:
                        # Case: Unknown
                        # Middle name not found in the first or last names ADS list
                        if default_to_last_name:
                            add_to_last.append(middle_name)
                            last_name_found = True
                        else:
                            add_to_first.append(middle_name)
            except Exception as e:
                logging.exception("Unexpected error in middle name parsing")
            author.first = [author.first] + add_to_first
            # [MT 2020 Oct 07, can't reproduce where .reverse() is necessary?]
            # add_to_last.reverse()
            author.last = add_to_last + [author.last]
        author.middle = u''

        # Verify that no first names appear in the detected last name
        if (author.last):
            if isinstance(author.last, basestring):
                last_name_list = [author.last]
            else:
                last_name_list = author.last.split()
            # At this point we already know it has at least 1 last name and
            # we will not question that one (in the last position)
            verified_last_name_list = [last_name_list.pop()]
            last_name_list.reverse()
            try:
                for last_name in last_name_list:
                    last_name_upper = last_name.upper()
                    if last_name_upper in self.first_names and last_name_upper not in self.last_names:
                        author.first = [author.first, last_name]
                    else:
                        verified_last_name_list.append(last_name)
            except Exception as err:
                logging.exception("Unexpected error in last name parsing")
            else:
                verified_last_name_list.reverse()
                author.last = verified_last_name_list

        try:
            reordered_author_str = str(author).strip()
        except Exception as err:
            logging.exception("Unexpected error converting detected name into a string")
            # TODO: Implement better error control
            reordered_author_str = self.unknown_author_str
        else:
            if len(reordered_author_str) == 0:
                reordered_author_str = self.unknown_author_str
        return unicode_entities(reordered_author_str).replace('  ', ' ')

    def parse(self, authors_str, normalize=False, delimiter=u';', default_to_last_name=True, collaborations_params={}):
        """
        Receives an authors string with individual author names separated by a
        delimiter and returns re-formatted authors string where all author
        names follow the structure: last name, first name

        It also verifies if an author name string contains a collaboration
        string.  The collaboration extraction can be controlled by the
        dictionary 'collaborations_params' which can have the following keys:

        - keywords [list of strings]: Keywords that appear in strings that
          should be identifier as collaboration strings. Default: 'group',
          'team', 'collaboration'
        - remove_the [boolean]: Remove the article 'The' from collaboration
          strings (e.g., 'The collaboration'). Default: False.
        - first_author_delimiter [string]: Some collaboration strings include
          the first author separated by a delimiter (e.g., The collaboration:
          First author), the delimiter can be specified in this variable,
          otherwise None or False values can be provided to avoid trying to
          extract first authors from collaboration strings. Default: ':'
        - fix_arXiv_mixed_collaboration_string [boolean]: Some arXiv entries
          mix the collaboration string with the collaboration string.
          (e.g. 'collaboration, Gaia'). Default: False
        """
        default_collaborations_params = self.default_collaborations_params.copy()
        default_collaborations_params.update(collaborations_params)
        collaborations_params = default_collaborations_params

        # Split and convert unicode characters and numerical HTML
        # (e.g. 'u'both em\u2014and&#x2013;dashes&hellip;' -> 'both em&mdash;and&ndash;dashes&hellip;')
        if sys.version_info > (3,):
            str_type = str
        else:
            str_type = unicode
        authors_list = [str_type(named_entities(n.strip())) for n in authors_str.split(delimiter)]

        corrected_authors_list = []
        for author_str in authors_list:
            author_str = self._clean_author_name(author_str)
            # Check for collaboration strings
            is_collaboration, collaboration_str = self._extract_collaboration(author_str, default_to_last_name, delimiter, collaborations_params)
            if is_collaboration:
                # Collaboration strings can contain the first author, which we need to split
                for corrected_author_str in collaboration_str.split(delimiter):
                    corrected_authors_list.append(corrected_author_str.strip())
            else:
                corrected_authors_list.append(self._reorder_author_name(author_str, default_to_last_name))
        corrected_authors_str = (delimiter + u' ').join(corrected_authors_list)

        # Last minute global corrections due to manually detected problems in
        # our processing corrected_authors_str =
        # corrected_authors_str.replace(' ,', ',').replace('  ', ' ').
        # replace('. -', '.-')
        corrected_authors_str = corrected_authors_str.replace(u', , ', u', ')
        corrected_authors_str = corrected_authors_str.replace(u' -', u'-').replace(u' ~', u'~')
        if normalize:
            return self._normalize(corrected_authors_str, delimiter=delimiter, collaborations_params=collaborations_params)
        else:
            return corrected_authors_str
