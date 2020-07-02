import os
import json
import requests


def find(key, dictionary):
    for k, v in dictionary.iteritems():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result


MONTH_TO_NUMBER = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                   'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11,
                   'dec': 12}

# APS Journal dictionary: used by parsers/aps.py to get the bibstem
APS_PUBLISHER_IDS = {'PRL': 'PhRvL', 'PRX': 'PhRvX', 'RMP': 'RvMP',
                     'PRA': 'PhRvA', 'PRB': 'PhRvB', 'PRC': 'PhRvC',
                     'PRD': 'PhRvD', 'PRE': 'PhRvE', 'PRAB': 'PhRvS',
                     'PRSTAB': 'PhRvS', 'PRAPPLIED': 'PhRvP',
                     'PRFLUIDS': 'PhRvF', 'PRMATERIALS': 'PhRvM',
                     'PRPER': 'PRPER', 'PRSTPER': 'PRSTP', 'PR': 'PhRv',
                     'PRI': 'PhRvI', 'PHYSICS': 'PhyOJ',
                     'PRResearch': 'PhRvR'}

IOP_PUBLISHER_IDS = {'apj': u'ApJ', 'jcap': u'JCAP', 'ejp': u'EJPh',
                     'raa': u'RAA', 'pmea': u'PhyM', 'd': u'JPhD',
                     'aj': u'AJ', 'apex': u'APExp', 'apjl': u'ApJL',
                     'apjs': u'ApJS', 'bb': u'BiBi', 'bf': u'BioFa',
                     'bmm': u'BioMa', 'cqg': u'CQGra', 'cpc': u'ChPhC',
                     'ctp': u'CoTPh', 'epl': u'EL', 'erc': u'ERCom',
                     'erx': u'ERExp', 'erl': u'ERL', 'est': u'EleSt',
                     'FCS': u'FCS', 'fdr': u'FlDyR', 'izv': u'IzMat',
                     'jbr': u'JBR', 'jopt': u'JOpt', 'cm': u'JPCM',
                     'jpenergy': u'JPEn', 'a': u'JPhA', 'b': u'JPhB',
                     'jpco': u'JPhCo', 'g': u'JPhG', 'jpmater': u'JPhM',
                     'jpphoton': u'JPhP', 'lpl': u'LaPhL', 'mrx': u'MRE',
                     'mst': u'MeScT', 'mfm': u'MuMat', 'njp': u'NJPh',
                     'nanoe': u'NanoE', 'nanof': u'NanoF', 'nano': u'Nanot',
                     'non': u'Nonli', 'pasp': u'PASP', 'met': u'Metro',
                     'pmb': u'PMB', 'ppcf': u'PPCF', 'prex': u'PRCom',
                     'ps': u'PhyS', 'ped': u'PhyEd',
                     'phu': u'PhyU', 'pst': u'PlST', 'prge': u'PrEne',
                     'rnaas': u'RNAAS', 'rop': u'RPPh', 'rms': u'RuMaS',
                     'sst': u'SeScT', 'sust': u'SuScT', 'tdm': u'TDM',
                     'rcr': u'RuCRv', 'nf': u'NucFu', 'jmm': u'JMiMi',
                     'cpl': u'ChPhL', 'ip': u'InvPr', 'jrp': u'JRP', 'psj': u'PSJ',
                     'psst': u'PSST', 'sms': u'SMaS', 'msms': u'MSMSE',
                     'qel': u'QuEle', 'msb': u'SbMat', 'jjap': u'JaJAP',
                     'ansn': u'ANSNN', 'maf': u'MApFl', 'stmp': u'SuTMP',
                     'qst': u'QS&T', 'ees': u'E&ES', 'mse': u'MS&E',
                     'pb': u'PhBio', 'lp': u'LaPhy', 'cpb': u'ChPhB',
                     'jos': u'JSemi', 'jne': u'JNEng', 'jge': u'JGE',
                     'jstat': u'JSMTE', 'jpcs': u'JPhCS', 'pw': u'PhyW',
                     'prv': u'PPS', 'jcv': u'JPhC', 'jphf': u'JPhF',
                     'jinst': u'JInst', 'ecst': u'ECSTr', 'jes': u'JElS',
                     'jss': u'JSSST'}

IOP_JOURNAL_NAMES = {'rnaas': u'Research Notes of the American Astronomical Society'}

# IOP_SPECIAL_ID_HANDLING = ['PASP.','QuEle','JGE..','PhyU.','IzMat','SbMat',
#                            'RuMaS','RuCRv','EL...','Nonli','JRP..']
IOP_SPECIAL_ID_HANDLING = ['PASP.']

OUP_PUBLISHER_IDS = {'mnras': u'MNRAS', 'mnrasl': u'MNRAS',
                     'pasj': u'PASJ', 'ptep': u'PTEP', 'gji': u'GeoJI'}
OUP_PDFDIR = 'https://academic.oup.com'

OUP_TMP_DIRS = {
    'mnrasl': '/proj/ads/abstracts/config/links//DOI/MNRASL',
    'mnras':  '/proj/ads/abstracts/config/links//DOI/MNRAS',
    'pasj.':  '/proj/ads/abstracts/config/links//DOI/PASJ',
    'gji':    '/proj/ads/abstracts/config/links//DOI/GeoJI'
}
    
AIP_PUBLISHER_IDS = {'AAIDBI': u'AIPA', 'APCPCS': u'AIPC', 'APPLAB': u'ApPhL',
                     'AMPADS': u'APLM', 'APPHD2': u'APLP', 'AQSVAT': u'AVSQS',
                     'APRPG5': u'ApPRv', 'CHAOEH': u'Chaos',
                     'JAPIAU': u'JAP', 'JCPSA6': u'JChPh', 'JMAPAQ': u'JMP',
                     'JPCRBU': u'JPCRD', 'LTPHEG': u'LTP', 'PHFLE6': u'PhFl',
                     'PHPAEN': u'PhPl', 'PHTEAH': u'PhTea', 'RSINAK': u'RScI'}

JATS_TAGS_DANGER = ['php', 'script', 'css']

JATS_TAGS_MATH = ['inline-formula',
                  'tex-math',
                  'sc',
                  'mml:math',
                  'mml:semantics',
                  'mml:mrow',
                  'mml:munder',
                  'mml:mo',
                  'mml:mi',
                  'mml:msub',
                  'mml:mover',
                  'mml:mn',
                  'mml:annotation'
                  ]

JATS_TAGS_HTML = ['sub', 'sup', 'a', 'astrobj']

JATS_TAGSET = {'title': JATS_TAGS_MATH + JATS_TAGS_HTML,
               'abstract': JATS_TAGS_MATH + JATS_TAGS_HTML + ['pre', 'br'],
               'comments': JATS_TAGS_MATH + JATS_TAGS_HTML + ['pre', 'br'],
               'affiliations': ['email', 'orcid'],
               'keywords': ['astrobj']
               }

# KEYWORDS

# Unified Astronomy Thesaurus
# retrieve current UAT from github
UAT_URL = 'https://raw.githubusercontent.com/astrothesaurus/UAT/master/UAT.json'
try:
    uat_request = requests.get(UAT_URL)
    UAT_ASTRO_KEYWORDS = list(find('name', uat_request.json()))
    # print("Info: loaded %s UAT keywords from github." % len(UAT_ASTRO_KEYWORDS))
except Exception as e:
    print("Warning: could not load UAT from github!")
    UAT_ASTRO_KEYWORDS = []

# American Physical Society keywords
APS_ASTRO_KEYWORDS_FILE = os.path.dirname(os.path.abspath(__file__)) + '/kw_aps_astro.dat'
APS_ASTRO_KEYWORDS = []
try:
    with open(APS_ASTRO_KEYWORDS_FILE, 'rU') as fk:
        for l in fk.readlines():
            APS_ASTRO_KEYWORDS.append(l.strip())
except Exception as e:
    print("Error loading APS Astro keywords: %s" % e)

# American Astronomical Society keywords (superseded June 2019 by UAT)
AAS_ASTRO_KEYWORDS_FILE = os.path.dirname(os.path.abspath(__file__)) + '/kw_aas_astro.dat'
AAS_ASTRO_KEYWORDS = []
try:
    with open(AAS_ASTRO_KEYWORDS_FILE, 'rU') as fk:
        for l in fk.readlines():
            AAS_ASTRO_KEYWORDS.append(l.strip())
except Exception as e:
    print("Error loading AAS Astro keywords: %s" % e)



# COMBINE ALL ASTRO KEYWORDS INTO AST_WORDS -- used by dbfromkw
AST_WORDS = UAT_ASTRO_KEYWORDS + APS_ASTRO_KEYWORDS + AAS_ASTRO_KEYWORDS

# REFERENCE SOURCE OUTPUT
REFERENCE_TOPDIR = '/proj/ads/references/sources/'

# REFSOURCE DICTIONARY
REFSOURCE_DICT = {
    'iop': 'iopft.xml',
    'oup': 'oupft.xml',
    'pnas': 'pnas.xml'
}

# AUTHOR ALIASES
AUTHOR_ALIAS_DIR = '/proj/ads/abstracts/config/Authors/'

# HTML_ENTITY_TABLE
HTML_ENTITY_TABLE = os.path.dirname(os.path.abspath(__file__)) + '/html5.dat'
ENTITY_DICTIONARY = dict()
try:
    with open(HTML_ENTITY_TABLE, 'rU') as fent:
        for l in fent.readlines():
            carr = l.rstrip().split('\t')

            UNI_ENTITY = None
            NAME_ENTITY = None
            HEX_ENTITY = None
            DEC_ENTITY = None
            if len(carr) >= 4:
                UNI_ENTITY = carr[0]
                NAME_ENTITY = carr[1]
                HEX_ENTITY = carr[2].lower()
                DEC_ENTITY = carr[3].lower()
                for c in NAME_ENTITY.strip().split():
                    try:
                        ENTITY_DICTIONARY[c.strip()] = DEC_ENTITY.strip()
                    except Exception as e:
                        print("Error splitting NAME_ENTITY: '%s'" % NAME_ENTITY)
                ENTITY_DICTIONARY[UNI_ENTITY.strip()] = DEC_ENTITY.strip()
                ENTITY_DICTIONARY[HEX_ENTITY.strip()] = DEC_ENTITY.strip()
            else:
                print("broken HTML entity:", l.rstrip())
                NAME_ENTITY = "xxxxx"

except Exception as e:
    print("Problem in config:", e)

# ADS-specific translations
# have been added to html5.txt
ENTITY_DICTIONARY['&sim;'] = "~"
ENTITY_DICTIONARY['&Tilde;'] = "~"
ENTITY_DICTIONARY['&rsquo;'] = "'"
ENTITY_DICTIONARY['&lsquo;'] = "'"
ENTITY_DICTIONARY['&nbsp;'] = " "
ENTITY_DICTIONARY['&mdash;'] = "-"
ENTITY_DICTIONARY['&ndash;'] = "-"
ENTITY_DICTIONARY['&rdquo;'] = '"'
ENTITY_DICTIONARY['&ldquo;'] = '"'
ENTITY_DICTIONARY['&minus;'] = "-"
ENTITY_DICTIONARY['&plus;'] = "+"
ENTITY_DICTIONARY['&thinsp;'] = " "
ENTITY_DICTIONARY['&hairsp;'] = " "
ENTITY_DICTIONARY['&ensp;'] = " "
ENTITY_DICTIONARY['&emsp;'] = " "


# ProQuest harvester
PROQUEST_OA_BASE = "http://pqdtopen.proquest.com/pubnum/%s.html"
PROQUEST_URL_BASE = "http://gateway.proquest.com/openurl?url_ver=Z39.88-2004&res_dat=xri:pqdiss&rft_val_fmt=info:ofi/fmt:kev:mtx:dissertation&rft_dat=xri:pqdiss:%s"
PROQUEST_DATASOURCE = "UMI"
PROQUEST_BIB_TO_PUBNUM_FILE = os.path.dirname(os.path.abspath(__file__)) + 'bibcode2pubno.dat'
PROQUEST_BIB_TO_PUBNUM = dict()
try:
    result = map(lambda b: PROQUEST_BIB_TO_PUBNUM.update({b[0]:b[1]}),
             map(lambda a: a.split(),
             open(PROQUEST_BIB_TO_PUBNUM_FILE).read().strip().split('\n')))
except Exception, err:
    pass

