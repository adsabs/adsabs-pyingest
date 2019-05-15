import sys
import re
from namedentities import named_entities, unicode_entities

import pyingest.config.config as config
from adsputils import u2asc

RE_INITIAL = re.compile('\. *(?!,)')
etal = re.compile(r",? et ?al\.?")
reand = re.compile(r" and ")
redash = re.compile(r"^-")
requot = re.compile(r"^'")

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



def _check_collab(authors_str, first_names, last_names, delimiter, default_to_last_name, collaborations_params):
    try:
        for s in collaborations_params['keywords']:
            if s in authors_str.lower():
                if collaborations_params['remove_the']:
                    outstring = authors_str.replace(u'The ', u'')
                else:
                    outstring = authors_str
                # if there's a ',' in the string, prob. incl. the 1st author
                string_list = outstring.split(',')
                if len(string_list) == 2:
                    string_list.reverse()
                    outstring = u' '.join(string_list).encode('utf-8')
                if collaborations_params['split']:
                    a_list = outstring.split(':')
                    a_split = []
                    for a in a_list:
                        if s in a.lower():
                            a_split.append(a.strip())
                        else:
                            a_split.append(_reorder_names(a.strip(), first_names, last_names, delimiter, default_to_last_name, collaborations_params))
                    a_list = [a.strip() for a in a_split]
                    outstring = (delimiter+u' ').join(a_list).encode('utf-8')
                return outstring.strip()
        return
    except Exception as e:
        print ("Error in _check_collab: ", e)
        return


def _reorder_names(authors_str, first_names, last_names, delimiter, default_to_last_name, collaborations_params):
    """
    """
    a = RE_INITIAL.sub('. ', authors_str)
    a = etal.sub('', a)
    a = reand.sub(' ', a)
    a = a.replace(' .', '.').replace('  ', ' ').replace(' ,',',')
    a = a.lstrip().rstrip().strip()
    collab_check = _check_collab(a, first_names, last_names, delimiter, default_to_last_name, collaborations_params)
    if collab_check is not None:
        return collab_check
    else:
        author = config.HumanName(a)
        if author.first == u'Jr.' and author.suffix != '':
            author.first = author.suffix
            author.suffix = u'Jr.'
        #print author.as_dict()


        if (author.middle):
            add_to_first = []
            add_to_last = []
            llast = False

            parts = author.middle.split()

            try:
                for subname in parts:
                    subup = subname.upper()
                    #if (len(subname.strip('.').strip('-')) <= 2 and subup not in last_names and "'" not in subname) or ((subup in first_names and subup not in last_names) or ((redash.sub('', subup)) in first_names and (redash.sub('', subup)) not in last_names) or ((requot.sub('', subup)) in first_names and (requot.sub('', subup)) not in last_names)):
                    #if (len(ads_ex.UNICODE_HANDLER.ent2u(subname).strip('.').strip('-')) <= 2 and subup not in last_names and "'" not in subname) or ((subup in first_names and subup not in last_names) or ((redash.sub('', subup)) in first_names and (redash.sub('', subup)) not in last_names) or ((requot.sub('', subup)) in first_names and (requot.sub('', subup)) not in last_names)):
                    if (len(unicode_entities(subname).strip('.').strip('-')) <= 2 and subup not in last_names and "'" not in subname) or ((subup in first_names and subup not in last_names) or ((redash.sub('', subup)) in first_names and (redash.sub('', subup)) not in last_names) or ((requot.sub('', subup)) in first_names and (requot.sub('', subup)) not in last_names)):
                        if llast:
                            add_to_last.reverse()
                            while add_to_last:
                                add_to_first.append(add_to_last.pop())
                            llast = False
                        add_to_first.append(subname)
                    elif (llast) or (subname.upper() in last_names):
                        add_to_last.append(subname)
                        llast = True
                    else:
                        if default_to_last_name:
                            add_to_last.append(subname)
                            llast = True
                        else:
                            add_to_first.append(subname)
            except Exception as e:
                print "exception in nameparsing: ", e
            author.middle = u''
            for name in add_to_first:
                author.first = [author.first, name]
            add_to_last.reverse()
            for name in add_to_last:
                author.last = [name, author.last]
        author.middle = u''

        # YOU NEED TO CHECK THAT NO FIRST NAMES APPEAR IN LAST
        if (author.last):
            parts = author.last.split()
            author_last_new = [parts[-1]]
            r_parts = parts[:-1]
            r_parts.reverse()
            try:
                for subname in r_parts:
                    if subname.upper() in first_names and subname.upper() not in last_names:
                        author.first = [author.first, subname]
                    else:
                        author_last_new.append(subname)
            except Exception as e:
                print "exception in nameparsing: ", e
            else:
                author_last_new.reverse()
                author.last = author_last_new

    try:
        auth_string = str(author)
    except:
        return "ERROR RETURNING NAME"
    else:
        #return auth_string.replace('  ', ' ')
        #return ads_ex.UNICODE_HANDLER.ent2u(auth_string).replace('  ', ' ')
        return unicode_entities(auth_string).replace('  ', ' ')


def ads_name_adjust(authors_str, delimiter=u';', default_to_last_name=True, collaborations_params={}):
    """
    Receives an authors string with individual author names separated by a
    delimiter and returns re-formatted authors string where all author names
    follow the structure: last name, first name
    """
    default_collaborations_params = {'keywords': ['group', 'team', 'collaboration'], 'split': True, 'remove_the': False}
    default_collaborations_params.update(collaborations_params)
    collaborations_params = default_collaborations_params

    author_list = authors_str.split(delimiter)
    author_list_clean = [named_entities(n) for n in author_list]
    # lists for pre- and post-nameparser comparison

    author_out = []
    for a in author_list_clean:
        for name in _reorder_names(a, first_names, last_names, delimiter, default_to_last_name, collaborations_params).split(delimiter):
            author_out.append(name)
        #outstring = (delimiter+u' ').join(author_out).replace(' ,', ',').replace('  ', ' ').replace('. -', '.-')
        outstring = (delimiter+u' ').join(author_out).replace(u', , ', u', ')
        outstring = outstring.replace(u' -', u'-').replace(u' ~', u'~')
    return outstring

