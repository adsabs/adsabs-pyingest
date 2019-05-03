import sys
import re
from namedentities import named_entities

try:
    import ads.ADSCachedExports as ads_ex
except ImportError:
    sys.path.append('/proj/ads/soft/python/lib/site-packages')
    try:
        import ads.ADSCachedExports as ads_ex
    except ImportError as e:
        print 'Unable to import ads libraries: {}'.format(e)


import pyingest.config.config as config
from adsputils import u2asc

etal = re.compile(r",? et ?al\.?")
reand = re.compile(r" and ")
redash = re.compile(r"^-")

first_names = []
last_names = []


def read_datfile(filename):
    output_list = []
    with open(filename,'rU') as fp:
        for l in fp.readlines():
            if l.strip() != '' and l[0] != '#':
                output_list.append(l.strip())
    return output_list


def init_namelists():

    try:
        first_names = read_datfile(config.FIRST_NAMES)
        last_names = read_datfile(config.LAST_NAMES)
        prefix_names = read_datfile(config.PREFIX_NAMES)
        suffix_names = read_datfile(config.SUFFIX_NAMES)
# try adding some extras?
        last_names.append('Y')
        last_names.append('O')
        first_names.append('Md')
    except Exception as e:
        raise BaseException(e)
    return first_names,last_names,prefix_names,suffix_names


def check_collab(instring,first_names,last_names):
    try:
        for s in config.COLLAB_STRINGS:
            if s in instring.lower():
                if config.COLLAB_REMOVE_THE:
                    outstring = instring.replace(u'The ',u'')
                else:
                    outstring = instring
                # if there's a ',' in the string, prob. incl. the 1st author
                string_list = outstring.split(',')
                if len(string_list) == 2:
                    string_list.reverse()
                    outstring = u' '.join(string_list).encode('utf-8')
                if config.COLLAB_SPLIT:
                    a_list = outstring.split(':')
                    a_split = []
                    for a in a_list:
                        if s in a.lower():
                            a_split.append(a.strip())
                        else:
                            a_split.append(reorder_names(a.strip(),first_names,last_names))
                    a_list = [a.strip() for a in a_split]
                    outstring = (config.AUTHOR_SEP+u' ').join(a_list).encode('utf-8')
                return outstring.strip()
        return
    except Exception as e:
        print ("Error in check_collab: ",e)
        return


def reorder_names(instring,first_names,last_names):
    a = ads_ex.RE_INITIAL.sub('. ', instring)
    a = etal.sub('',a)
    a = reand.sub(' ',a)
    a = a.replace(' .','.').replace('  ',' ').replace(' ,',',')
    a = a.lstrip().rstrip().strip()
    collab_check = check_collab(a,first_names,last_names)
    if collab_check is not None:
        return collab_check
    else:
        author = config.HumanName(a)
        if author.first == u'Jr.' and author.suffix != '':
            author.first = author.suffix
            author.suffix = u'Jr.'
        print author.as_dict()
        

        if (author.middle):
            add_to_first = []
            add_to_last = []
            llast = False

            parts = author.middle.split()

            try:
                for subname in parts:
                    subup = subname.upper()
#                   if (len(ads_ex.UNICODE_HANDLER.ent2u(subname).strip('.').strip('-')) <= 2 and subup not in last_names and "'" not in subname) or (subup in first_names and subup not in last_names):
                    if (len(ads_ex.UNICODE_HANDLER.ent2u(subname).strip('.').strip('-')) <= 2 and subup not in last_names and "'" not in subname) or ((subup in first_names and subup not in last_names) or ((redash.sub('',subup)) in first_names and (redash.sub('',subup)) not in last_names)):
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
                        if (config.PRIORITY_LAST):
                            add_to_last.append(subname)
                            llast = True
                        else:
                            add_to_first.append(subname)
            except Exception as e:
                print "exception in nameparsing: ",e
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
                print "exception in nameparsing: ",e
            else:
                author_last_new.reverse()
                author.last = author_last_new
                
    try:
        auth_string = str(author)
    except:
        return "ERROR RETURNING NAME"
    else:
        return ads_ex.UNICODE_HANDLER.ent2u(auth_string).replace('  ',' ')


def ads_name_adjust(instring):
    
# assumes 'instring' is in standardized name format, with individual authors
# separated by semicolons

    try:
        (first_names, last_names, prefix_names, suffix_names) = init_namelists()
        for s in prefix_names:
            config.CONSTANTS.titles.add(s)
        for s in suffix_names:
            config.CONSTANTS.suffix_acronyms.add(s)
            config.CONSTANTS.suffix_not_acronyms.add(s)
    except Exception as e:
        first_names = []
        last_names = []

    author_list = instring.split(config.AUTHOR_SEP)
    author_list_clean = [named_entities(n) for n in author_list]
#   lists for pre- and post-nameparser comparison

    author_out = []
    for a in author_list_clean:
        for name in reorder_names(a,first_names,last_names).split(';'):
            author_out.append(name)
#       outstring = '; '.join(author_out).replace(' ,',',').replace('  ',' ').replace('. -','.-')
        outstring = '; '.join(author_out).replace(', , ',', ')
        outstring = outstring.replace(' -','-').replace(' ~','~')
    return outstring

