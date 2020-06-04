#!/usr/bin/env python

import sys
import os
import json
import codecs
import string
from adsputils import u2asc
from jats import JATSParser
from pyingest.config.config import *
from pyingest.parsers.entity_convert import EntityConverter
from author_names import AuthorNames

class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass

class UnparseableException(Exception):
    pass


class OUPJATSParser(JATSParser):

<<<<<<< HEAD
=======
    AST_WORDS = [x.lower() for x in UAT_ASTRO_KEYWORDS]
    AST_WORDS = AST_WORDS + [x.lower() for x in AAS_ASTRO_KEYWORDS]
    AST_WORDS = AST_WORDS + [x.lower() for x in APS_ASTRO_KEYWORDS]


>>>>>>> config.py and oup.py changes
    def get_author_init(self,namestring):
        output = u2asc(namestring)
        for c in output:
            if c.isalpha():
                return c.upper()
        return u'.'

    def oup_journals(self, pid):
        try:
            bibstem = OUP_PUBLISHER_IDS[pid]
        except KeyError:
            return 'XSTEM'
        else:
            return bibstem

    def get_tmp_page(self, bs):
<<<<<<< HEAD
        try:
            f = OUP_TMP_DIRS[bs.lower()]
        except:
            pass
        else:
            f = f + "early.dat.nocheck"
            try:
                with open(f,'rU') as fp:
                    p = fp.readline()
                return p.split()[0]
            except Exception, err:
                pass

    def update_tmp_file(self, bs, bib, doi):
        try:
            f = OUP_TMP_DIRS[bs.lower()]
        except:
            pass
        else:
            f = f + "early.dat.nocheck"
            l = bib + "\t" + doi + "\n"
            try:
                with open(f,'a') as fp:
                    fp.write(l)
                # now replace first line
                c = bib[14:18]
                c = c.replace('.','')
                c = c + "\n"
                with open(f,'r') as fp:
                    lines = fp.readlines()
                    lines[0] = c
                with open(f,'w') as fp:
                    lines = fp.writelines(lines)
            except Exception, err:
                pass
=======
        if(bs.lower() == 'mnrasl'):
            f = "/proj/ads/abstracts/config/links//DOI/MNRASL"
        elif(bs.lower() == 'mnras'):
            f = "/proj/ads/abstracts/config/links//DOI/MNRAS"
        elif(bs.lower() == 'gji'):
            f = "/proj/ads/abstracts/config/links//DOI/GeoJI"
        f = f + "early.dat.nocheck"
        with open(f,'rU') as fp:
            p = fp.readline()
        return p.split()[0]


    def update_tmp_file(self, bs, bib, doi):
        if(bs.lower() == 'mnrasl'):
            f = "/proj/ads/abstracts/config/links//DOI/MNRASL"
        elif(bs.lower() == 'mnras'):
            f = "/proj/ads/abstracts/config/links//DOI/MNRAS"
        elif(bs.lower() == 'gji'):
            f = "/proj/ads/abstracts/config/links//DOI/GeoJI"
        f = f + "early.dat.nocheck"
        l = bib + "\t" + doi + "\n"
        with open(f,'a') as fp:
            fp.write(l)
        # now replace first line
        c = bib[14:18]
        c = c.replace('.','')
        c = c + "\n"
        with open(f,'r') as fp:
            lines = fp.readlines()
            lines[0] = c
        with open(f,'w') as fp:
            lines = fp.writelines(lines)
>>>>>>> config.py and oup.py changes

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


<<<<<<< HEAD
=======
    def getrefs(self, refs):
        refs = dict()
#       try:
#           refs = document.back
#       except:
#           pass
        return refs


>>>>>>> config.py and oup.py changes
    def parse(self, fp, **kwargs):

        output_metadata = super(self.__class__, self).parse(fp, **kwargs)

<<<<<<< HEAD
        # Publication +
=======
        fp.seek(0)
        document = self.resource_dict(fp, **kwargs)


# Publication +
>>>>>>> config.py and oup.py changes
	isearly = 0
	try:
            pubstring = output_metadata['publication']
        except Exception, err:
            pass
        else:
            try:
                output_metadata['volume']
            except Exception, err:
                pass
            else:
                if output_metadata['volume'] == "None":
                    pubstring = pubstring +', Advance Access'
                    isearly = 1
                else:
                    pubstring = pubstring +', Volume '+ output_metadata['volume']
            
                    try:
                        output_metadata['issue']
                    except TypeError:
                        pass
                    else:
                        pubstring = pubstring +', Issue '+ output_metadata['issue']

                    try:
                        output_metadata['page']
                    except Exception, err:
                        pass
                    else:
                        if "-" in output_metadata['page']:
                            pubstring = pubstring + ', pp.' + output_metadata['page']
                        else:
                            pubstring = pubstring + ', id.' + output_metadata['page']

            output_metadata['publication'] = pubstring
            
<<<<<<< HEAD
        # Bibcode
=======
# Bibcode
>>>>>>> config.py and oup.py changes
        try:
            j_bibstem = self.oup_journals(output_metadata['pub-id'])
        except KeyError:
            pass
        else:
            year = output_metadata['pubdate'][-4:]
            bibstem = j_bibstem.ljust(5,'.')
            if isearly:
                if 'Letter' in pubstring:
                    issue_letter = "L"
                    bibstem = "MNRASL"
                else:
                    issue_letter = "."
                idno = self.get_tmp_page(bibstem)
                try:
                    idno = int(idno) + 1
                except Exception, err: 
                    print "Issue with tmp bibstem:",err,idno
                idno = str(idno)
                idno = idno.rjust(4,'.')
                volume = ".tmp"
            else:
                volume = output_metadata['volume'].rjust(4,'.')
                if output_metadata['pub-id'] == 'ptep':
                    issue_letter = string.letters[int(output_metadata['issue'])-1]
                    idno = output_metadata['page']
                    if len(idno) == 6:
                        try:
                            idtwo = string.letters[int(idno[0:2]) - 1]
                        except Exception, err:
                            idtwo = idno[0:2]
                        idfour = idno[2:]
                    else:
                        idtwo = ''
                        idfour = idno.rjust(4,'.')
                    idno = idfour
                elif output_metadata['pub-id'] == 'mnrasl':
                    issue_letter = 'L'
                    if output_metadata['page'].find("-"):
                        idno = output_metadata['page'].split("-")[0]
                    else:
                        idno = output_metadata['page']
                    idno = idno.lstrip(idno[:1])
                    idno = idno.rjust(4,'.')
                else:
                    issue_letter = '.'
                    if output_metadata['page'].find("-"):
                        idno = output_metadata['page'].split("-")[0]
                    else:
                        idno = output_metadata['page']
                    idno = idno.rjust(4,'.')
            try:
<<<<<<< HEAD
=======
            #   author_init = self.get_author_init(output_metadata['authors'][0])
>>>>>>> config.py and oup.py changes
                author_init = self.get_author_init(output_metadata['authors'])
            except Exception, err:
                author_init = '.'
            # would be better if I had two different variables for bibstem (since MNRASL shares a bibstem with MNRAS)
            if bibstem == "MNRASL":
                bibstem = "MNRAS"
            output_metadata['bibcode'] = year + bibstem + volume + issue_letter + idno + author_init
            if issue_letter == 'L':
                bibstem = "MNRASL"
<<<<<<< HEAD
            if isearly:
=======
            if( isearly ):
>>>>>>> config.py and oup.py changes
                v = self.update_tmp_file(bibstem,output_metadata['bibcode'],output_metadata['properties']['DOI'])
                del output_metadata['page']
                isearly = 0

        if 'DOI' in output_metadata['properties']:
<<<<<<< HEAD
            plink = "/".join(["https:/","academic.oup.com",output_metadata['pub-id'],"pdf_lookup","doi",output_metadata['properties']['DOI']])
=======
            plink = "/".join(["https:/","academic.oup.com",output_metadata['pub-id'],"pdf_lookup",output_metadata['properties']['DOI']])
>>>>>>> config.py and oup.py changes
            output_metadata['properties'].update({'PDF': plink})

        # pass relevant fields through EntityConverter
        # to remove bad entities
<<<<<<< HEAD
        entity_fields = ['abstract', 'title', 'authors']
=======
        # entity_fields = ['abstract', 'title', 'authors', 'affiliations']
        entity_fields = ['abstract', 'title', 'authors']
        # entity_fields = ['abstract', 'title']
>>>>>>> config.py and oup.py changes
        for ecf in entity_fields:
            if ecf in output_metadata.keys():
                try:
                    conv = EntityConverter()
                    conv.input_text = output_metadata[ecf]
                    conv.convert()
                    output_metadata[ecf] = conv.output_text
                except Exception, err:
                    print "problem converting %s for %s: %s" % (ecf, output_metadata['bibcode'], err)

        # Return
        return output_metadata

