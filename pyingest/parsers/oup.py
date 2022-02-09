#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import string
from .jats import JATSParser
from .author_init import AuthorInitial
from pyingest.config.config import *


class NoSchemaException(Exception):
    pass


class WrongSchemaException(Exception):
    pass


class UnparseableException(Exception):
    pass


class OUPJATSParser(JATSParser):

    def oup_journals(self, pid):
        try:
            bibstem = OUP_PUBLISHER_IDS[pid]
        except KeyError:
            return 'XSTEM'
        else:
            return bibstem

    def get_tmp_page(self, bs):
        try:
            f = OUP_TMP_DIRS[bs.lower()]
        except Exception as err:
            pass
        else:
            f = f + "early.dat.nocheck"
            try:
                if sys.version_info > (3,):
                    open_mode = 'rb'
                else:
                    open_mode = 'rU'
                with open(f, open_mode) as fp:
                    p = fp.readline()
                return p.split()[0]
            except Exception as err:
                pass

    def update_tmp_file(self, bs, bib, doi):
        try:
            f = OUP_TMP_DIRS[bs.lower()]
        except Exception as err:
            pass
        else:
            f = f + "early.dat.nocheck"
            l = bib + "\t" + doi + "\n"
            try:
                with open(f, 'a') as fp:
                    fp.write(l)
                # now replace first line
                c = bib[14:18]
                c = c.replace('.', '')
                c = c + "\n"
                with open(f, 'r') as fp:
                    lines = fp.readlines()
                    # if you're replacing the first line, this is fine
                    lines[0] = c
                    # if you want to insert something before the first line,
                    # use this:
                    # lines.insert(0, c)
                with open(f, 'w') as fp:
                    # writelines doesn't need a return value, and doing this
                    # will destroy lines after it's done.
                    # lines = fp.writelines(lines)
                    fp.writelines(lines)
            except Exception as err:
                pass

    def dbfrombs(self, bs):
        db = []
        try:
            bibs = OUP_PUBLISHER_IDS[bs]
        except KeyError:
            return 'XSTEM'
        else:
            if bibs == 'ptep':
                database = "PHY"
            elif bibs == 'gji':
                database = "PHY"
            else:
                database = "AST"
        return database

    def getnexttmp(self, bs):
        tmpid = []
        try:
            bibs = OUP_PUBLISHER_IDS[bs]
        except KeyError:
            return 'XSTEM'
        else:
            database = "PHY"
        return tmpid

    def parse(self, input_data, **kwargs):

        output_metadata = super(self.__class__, self).parse(input_data, **kwargs)

        # Publication +
        isearly = 0
        try:
            pubstring = output_metadata['publication']
        except Exception as err:
            pass
        else:
            try:
                output_metadata['volume']
            except Exception as err:
                pass
            else:
                if output_metadata['volume'] == "None":
                    pubstring = pubstring + ', Advance Access'
                    isearly = 1
                else:
                    pubstring = pubstring + ', Volume ' + output_metadata['volume']

                    try:
                        output_metadata['issue']
                    except TypeError:
                        pass
                    else:
                        pubstring = pubstring + ', Issue ' + output_metadata['issue']

                    try:
                        output_metadata['page']
                    except Exception as err:
                        pass
                    else:
                        if "-" in output_metadata['page']:
                            pubstring = pubstring + ', pp.' + output_metadata['page']
                        else:
                            pubstring = pubstring + ', id.' + output_metadata['page']
                            if 'numpages' in output_metadata:
                                pubstring = pubstring + ', ' + output_metadata['numpages'] + ' pp.'
                                del(output_metadata['numpages'])

            output_metadata['publication'] = pubstring
            
        # Bibcode
        try:
            j_bibstem = self.oup_journals(output_metadata['pub-id'])
        except KeyError:
            pass
        else:
            year = output_metadata['pubdate'][-4:]
            bibstem = j_bibstem.ljust(5, '.')
            if isearly:
                if 'Letter' in pubstring:
                    issue_letter = "L"
                    bibstem = "MNRASL"
                else:
                    issue_letter = "."
                idno = self.get_tmp_page(bibstem)
                try:
                    idno = int(idno) + 1
                except Exception as err: 
                    print("Issue with tmp bibstem:", err, idno)
                idno = str(idno)
                idno = idno.rjust(4, '.')
                volume = ".tmp"
            else:
                volume = output_metadata['volume'].rjust(4, '.')
                if output_metadata['pub-id'] == 'ptep':
                    issue_letter = string.ascii_letters[int(output_metadata['issue'])-1]
                    idno = output_metadata['page']
                    if len(idno) == 6:
                        try:
                            idtwo = string.ascii_letters[int(idno[0:2]) - 1]
                        except Exception as err:
                            idtwo = idno[0:2]
                        idfour = idno[2:]
                    else:
                        idtwo = ''
                        idfour = idno.rjust(4, '.')
                    idno = idfour
                elif output_metadata['pub-id'] == 'mnrasl':
                    issue_letter = 'L'
                    if output_metadata['page'].find("-"):
                        idno = output_metadata['page'].split("-")[0]
                    else:
                        idno = output_metadata['page']
                    if idno.startswith("L"): 
                        idno = idno.lstrip(idno[:1])
                    idno = idno.rjust(4, '.')
                else:
                    issue_letter = '.'
                    if output_metadata['page'].find("-"):
                        idno = output_metadata['page'].split("-")[0]
                    else:
                        idno = output_metadata['page']
                    idno = idno.rjust(4, '.')
            try:
                a = AuthorInitial()
                author_init = a.get_author_init(output_metadata['authors'])
            except Exception as err:
                print(err)
                author_init = '.'
            # would be better if I had two different variables for bibstem (since MNRASL shares a bibstem with MNRAS)
            if bibstem == "MNRASL":
                bibstem = "MNRAS"
            output_metadata['bibcode'] = year + bibstem + volume + issue_letter + idno + author_init
            if issue_letter == 'L':
                bibstem = "MNRASL"
            if isearly:
                v = self.update_tmp_file(bibstem, output_metadata['bibcode'], output_metadata['properties']['DOI'])
                del output_metadata['page']
                isearly = 0

        if 'DOI' in output_metadata['properties']:
            plink = "/".join(["https:/", "academic.oup.com", output_metadata['pub-id'], "pdf-lookup", "doi",
                              output_metadata['properties']['DOI']])
            output_metadata['properties'].update({'PDF': plink})

        # Return
        return output_metadata
