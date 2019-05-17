import sys
import re
import logging
from namedentities import named_entities, unicode_entities

import pyingest.config.config as config
from adsputils import u2asc

regex_initial = re.compile('\. *(?!,)')
regex_etal = re.compile(r",? et ?al\.?")
regex_and = re.compile(r" and ")
regex_dash = re.compile(r"^-")
regex_quote = re.compile(r"^'")
regex_the = re.compile(r"^[Tt]he ")

first_names = []
last_names = []

def _read_datfile(filename):
    output_list = []
    with open(filename, 'rU') as fp:
        for l in fp.readlines():
            if l.strip() != '' and l[0] != '#':
                output_list.append(l.strip())
    return output_list

try:
    first_names = _read_datfile(config.FIRST_NAMES)
    last_names = _read_datfile(config.LAST_NAMES)
    prefix_names = _read_datfile(config.PREFIX_NAMES)
    suffix_names = _read_datfile(config.SUFFIX_NAMES)
    # try adding some extras?
    last_names.append('Y')
    # removed 'O' by request of CSG -- failing more often than not
    #   last_names.append('O')
    first_names.append('Md')
    for s in prefix_names:
        config.CONSTANTS.titles.add(s)
    for s in suffix_names:
        config.CONSTANTS.suffix_acronyms.add(s)
        config.CONSTANTS.suffix_not_acronyms.add(s)
except Exception as e:
    raise BaseException(e)



def _extract_collaboration(collaboration_str, first_names, last_names, default_to_last_name, delimiter, collaborations_params):
    """
    Verifies if the author name string contains a collaboration string
    The collaboration extraction can be controlled by the dictionary
    'collaborations_params'.
    """
    corrected_collaboration_str = u'' # Default
    try:
        for keyword in collaborations_params['keywords']:
            if keyword in collaboration_str.lower():
                if collaborations_params['remove_the']:
                    corrected_collaboration_str = regex_the.sub(u'', collaboration_str)
                else:
                    corrected_collaboration_str = collaboration_str

                if collaborations_params['fix_arXiv_mixed_collaboration_string']:
                    ## TODO: Think a better way to account for this specific cases
                    # if there's a ',' in the string, it probably includes the 1st author
                    string_list = corrected_collaboration_str.split(',')
                    if len(string_list) == 2:
                        # Based on an arXiv author case: "collaboration, Gaia"
                        string_list.reverse()
                        corrected_collaboration_str = u' '.join(string_list).encode('utf-8')

                if collaborations_params['first_author_delimiter']:
                    # Based on an arXiv author case: "<tag>Collaboration: Name, Author</tag>"
                    authors_list = corrected_collaboration_str.split(collaborations_params['first_author_delimiter'])
                    corrected_authors_list = []
                    for author in authors_list:
                        if keyword in author.lower():
                            corrected_authors_list.append(author.strip())
                        else:
                            corrected_authors_list.append(_reorder_author_name(author.strip(), first_names, last_names, default_to_last_name))
                    corrected_collaboration_str = (delimiter+u' ').join(corrected_authors_list).strip().encode('utf-8')
                break
    except Exception as e:
        logging.exception("Unexpected error in collaboration checks")
    is_collaboration_str = corrected_collaboration_str != u''
    return is_collaboration_str, corrected_collaboration_str

def _clean_author_name(author_str):
    """
    Remove useless characters in author name string
    """
    author_str = regex_initial.sub('. ', author_str)
    author_str = regex_etal.sub('', author_str)
    author_str = regex_and.sub(' ', author_str)
    author_str = author_str.replace(' .', '.').replace('  ', ' ').replace(' ,',',')
    author_str = author_str.strip()
    return author_str

def _reorder_author_name(author_str, first_names, last_names, default_to_last_name):
    """
    Automatically detect first and last names in an author name string and reorder
    using the format: last name, first name
    """
    author = config.HumanName(author_str)
    if author.first == u'Jr.' and author.suffix != '':
        author.first = author.suffix
        author.suffix = u'Jr.'

    if (author.middle):
        # Move middle names to first name if detected as so,
        # or move to last name if detected as so
        # or move to the default
        add_to_first = []
        add_to_last = []
        last_name_found = False

        middle_name_list = author.middle.split()

        try:
            for middle_name in middle_name_list:
                middle_name_length = len(unicode_entities(middle_name).strip('.').strip('-')) # Ignore '.' or '-' at the beginning/end of the string
                middle_name_upper = middle_name.upper()
                if (middle_name_length <= 2 and middle_name_upper not in last_names and "'" not in middle_name) \
                    or (middle_name_upper in first_names and middle_name_upper not in last_names) \
                    or (regex_dash.sub('', middle_name_upper) in first_names and regex_dash.sub('', middle_name_upper) not in last_names) \
                    or (regex_quote.sub('', middle_name_upper) in first_names and regex_quote.sub('', middle_name_upper) not in last_names):
                        ## Case: First name found
                        # Middle name is found in the first names ADS list and not in the last names ADS list
                        if last_name_found:
                            # Move all previously detected first names to last name
                            # since we are in a situation where we detected:
                            # F F L F
                            # hence we correct it to:
                            # L L L F
                            # where F is first name and L is last name
                            add_to_first += add_to_last
                            add_to_last = []
                            last_name_found = False
                        add_to_first.append(middle_name)
                elif last_name_found or middle_name.upper() in last_names:
                    ## Case: Last name found
                    add_to_last.append(middle_name)
                    last_name_found = True
                else:
                    ## Case: Unknown
                    # Middle name not found in the first or last names ADS list
                    if default_to_last_name:
                        add_to_last.append(middle_name)
                        last_name_found = True
                    else:
                        add_to_first.append(middle_name)
        except Exception as e:
            logging.exception("Unexpected error in middle name parsing")
        author.first = [author.first] + add_to_first
        add_to_last.reverse()
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
                if last_name_upper in first_names and last_name_upper not in last_names:
                    author.first = [author.first, last_name]
                else:
                    verified_last_name_list.append(last_name)
        except Exception as e:
            logging.exception("Unexpected error in last name parsing")
        else:
            verified_last_name_list.reverse()
            author.last = verified_last_name_list

    try:
        reordered_author_str = str(author)
    except:
        logging.exception("Unexpected error converting detected name into a string")
        # TODO: Implement better error control
        return "ERROR RETURNING NAME"
    else:
        return unicode_entities(reordered_author_str).replace('  ', ' ')


def ads_name_adjust(authors_str, delimiter=u';', default_to_last_name=True, collaborations_params={}):
    """
    Receives an authors string with individual author names separated by a
    delimiter and returns re-formatted authors string where all author names
    follow the structure: last name, first name

    It also verifies if an author name string contains a collaboration string.
    The collaboration extraction can be controlled by the dictionary
    'collaborations_params' which can have the following keys:

    - keywords [list of strings]: Keywords that appear in strings that should be
    identifier as collaboration strings. Default: 'group', 'team', 'collaboration'
    - remove_the [boolean]: Remove the article 'The' from collaboration strings
    (e.g., 'The collaboration'). Default: False.
    - first_author_delimiter [string]: Some collaboration strings include the first
    author separated by a delimiter (e.g., The collaboration: First author), the
    delimiter can be specified in this variable, otherwise None or False values
    can be provided to avoid trying to extract first authors from collaboration
    strings. Default: ':'
    - fix_arXiv_mixed_collaboration_string [boolean]: Some arXiv entries mix the
    collaboration string with the collaboration string.
    (e.g. 'collaboration, Gaia'). Default: True
    """
    default_collaborations_params = {
        'keywords': ['group', 'team', 'collaboration'],
        'first_author_delimiter': ':',
        'remove_the': False,
        'fix_arXiv_mixed_collaboration_string': True,
    }
    default_collaborations_params.update(collaborations_params)
    collaborations_params = default_collaborations_params

    # Split and convert unicode characters and numerical HTML
    # (e.g. 'u'both em\u2014and&#x2013;dashes&hellip;' -> 'both em&mdash;and&ndash;dashes&hellip;')
    authors_list = [unicode(named_entities(n)) for n in authors_str.split(delimiter)]

    corrected_authors_list = []
    for author_str in authors_list:
        author_str = _clean_author_name(author_str)
        # Check for collaboration strings
        is_collaboration, collaboration_str = _extract_collaboration(author_str, first_names, last_names, default_to_last_name, delimiter, collaborations_params)
        if is_collaboration:
            # Collaboration strings can contain the first author, which we need to split
            for corrected_author_str in collaboration_str.split(delimiter):
                corrected_authors_list.append(corrected_author_str)
        else:
            corrected_authors_list.append(_reorder_author_name(author_str, first_names, last_names, default_to_last_name))
    corrected_authors_str = (delimiter+u' ').join(corrected_authors_list)

    # Last minute global corrections due to manually detected problems in our processing
    #corrected_authors_str = corrected_authors_str.replace(' ,', ',').replace('  ', ' ').replace('. -', '.-')
    corrected_authors_str = corrected_authors_str.replace(u', , ', u', ')
    corrected_authors_str = corrected_authors_str.replace(u' -', u'-').replace(u' ~', u'~')
    return corrected_authors_str

