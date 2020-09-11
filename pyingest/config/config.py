from __future__ import print_function
import os
import json
import requests


def get_uat(data,data_dict):
    if isinstance(data,dict):
        try:
            data_dict[data['name'].strip()] = data['uri'].strip().split('/')[-1]
        except:
            pass
        try:
            data['children']
        except:
            pass
        else:
            get_uat(data['children'],data_dict)
    elif isinstance(data,list):
        for n in data:
            get_uat(n,data_dict)


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
                     'fcs': u'FCS', 'fdr': u'FlDyR', 'izv': u'IzMat',
                     'jbr': u'JBR', 'jopt': u'JOpt', 'cm': u'JPCM',
                     'jpenergy': u'JPEn', 'a': u'JPhA', 'b': u'JPhB',
                     'jpco': u'JPhCo', 'jpcomplex': u'JPCom', 
                     'iopsn': u'IOPSN', 'g': u'JPhG', 'jpmater': u'JPhM',
                     'jpphoton': u'JPhP', 'lpl': u'LaPhL', 'mrx': u'MRE',
                     'mst': u'MeScT', 'mfm': u'MuMat', 'nanoe': u'NanoE',
                     'njp': u'NJPh', 'nanof': u'NanoF', 'nano': u'Nanot',
                     'non': u'Nonli', 'pasp': u'PASP', 'met': u'Metro',
                     'pmb': u'PMB', 'ppcf': u'PPCF', 'prex': u'PRCom',
                     'ps': u'PhyS', 'ped': u'PhyEd', 'psj': u'PSJ',
                     'phu': u'PhyU', 'pst': u'PlST', 'prge': u'PrEne',
                     'rnaas': u'RNAAS', 'rop': u'RPPh', 'rms': u'RuMaS',
                     'sst': u'SeScT', 'sust': u'SuScT', 'tdm': u'TDM',
                     'rcr': u'RuCRv', 'nf': u'NucFu', 'jmm': u'JMiMi',
                     'cpl': u'ChPhL', 'ip': u'InvPr', 'jrp': u'JRP',
                     'psst': u'PSST', 'sms': u'SMaS', 'msms': u'MSMSE',
                     'qel': u'QuEle', 'msb': u'SbMat', 'jjap': u'JaJAP',
                     'ansn': u'ANSNN', 'maf': u'MApFl', 'stmp': u'SuTMP',
                     'qst': u'QS&T', 'ees': u'E&ES', 'mse': u'MS&E',
                     'pb': u'PhBio', 'lp': u'LaPhy', 'cpb': u'ChPhB',
                     'jos': u'JSemi', 'jne': u'JNEng', 'jge': u'JGE',
                     'jstat': u'JSMTE', 'jpcs': u'JPhCS', 'pw': u'PhyW',
                     'prv': u'PPS', 'c': 'JPhC', 'jphf': 'JPhF',
                     'ecst': u'ECSTR', 'jinst': u'JInst', 'nanox': u'NanoE'}

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
    'geoji':    '/proj/ads/abstracts/config/links//DOI/GeoJI'
}

AIP_PUBLISHER_IDS = {'AAIDBI': u'AIPA', 'APCPCS': u'AIPC', 'APPLAB': u'ApPhL',
                     'aipa': u'AIPA', 'apc': u'AIPC', 'apl': u'APL',
                     'AMPADS': u'APLM', 'APPHD2': u'APLP', 'AQSVAT': u'AVSQS',
                     'apm': u'APLM', 'app': u'APLP', 'aqs': u'AVSQS',
                     'AJPIAS': u'AmJPh', 'APRPG5': u'ApPRv', 'CHAOEH': u'Chaos',
                     'ajp': u'AmJPh', 'are': u'ApPRv', 'cha': u'Chaos',
                     'JAPIAU': u'JAP', 'JCPSA6': u'JChPh', 'JMAPAQ': u'JMP',
                     'jap': u'JAP', 'jcp': u'JChPh', 'jmp': u'JMP',
                     'JPCRBU': u'JPCRD', 'LTPHEG': u'LTP', 'PHFLE6': u'PhFl',
                     'jpr': u'JPCRD', 'ltp': u'LTP', 'phl': u'PhFl',
                     'PHPAEN': u'PhPl', 'PHTEAH': u'PhTea', 'RSINAK': u'RScI',
                     'php': u'PhPl', 'pte': u'PhTea', 'rsi': u'RScI'}


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
UAT_ASTRO_URI_DICT = dict()
try:
    uat_request = requests.get(UAT_URL)
    uat_data = uat_request.json()
    get_uat(uat_request.json(), UAT_ASTRO_URI_DICT)
    UAT_ASTRO_KEYWORDS = list(UAT_ASTRO_URI_DICT.keys())
    UAT_ASTRO_URI_DICT = dict((k.lower(),v) for k,v in list(UAT_ASTRO_URI_DICT.items()))
except Exception as e:
    print("Warning: could not load UAT from github!")
    UAT_ASTRO_KEYWORDS = list()

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
                print(("broken HTML entity:", l.rstrip()))
                NAME_ENTITY = "xxxxx"

except Exception as e:
    print(("Problem in config:", e))

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
PROQUEST_BASE_PATH = "/proj/ads/abstracts/sources/ProQuest/fromProQuest/"
PROQUEST_OA_BASE = "http://pqdtopen.proquest.com/pubnum/%s.html"
PROQUEST_URL_BASE = "http://gateway.proquest.com/openurl?url_ver=Z39.88-2004&res_dat=xri:pqdiss&rft_val_fmt=info:ofi/fmt:kev:mtx:dissertation&rft_dat=xri:pqdiss:%s"
PROQUEST_DATASOURCE = "UMI"
PROQUEST_BIB_TO_PUBNUM_FILE = os.path.dirname(os.path.abspath(__file__)) + 'bibcode2pubno.dat'
PROQUEST_BIB_TO_PUBNUM = dict()
try:
    result = [PROQUEST_BIB_TO_PUBNUM.update({b[0]:b[1]}) for b in [a.split() for a in open(PROQUEST_BIB_TO_PUBNUM_FILE).read().strip().split('\n')]]
except Exception as err:
    pass

PROQUEST_TO_DB = {
    "African American Studies":"GEN",
    "Aeronomy":"PHY",
    "Agriculture, Agronomy":"GEN",
    "Agriculture, Animal Culture and Nutrition":"GEN",
    "Agriculture, Fisheries and Aquaculture":"GEN",
    "Agriculture, Food Science and Technology":"GEN",
    "Agriculture, Forestry and Wildlife":"GEN",
    "Agriculture, General":"GEN",
    "Agriculture, Horticulture":"GEN",
    "Agriculture, Plant Culture":"GEN",
    "Agriculture, Plant Pathology":"GEN",
    "Agriculture, Range Management":"GEN",
    "Agriculture, Soil Science":"GEN",
    "Agriculture, Wildlife Conservation":"GEN",
    "Agriculture, Wood Technology":"GEN",
    "Alternative Energy":"PHY",
    "American Studies":"GEN",
    "Anthropology, Archaeology":"GEN",
    "Anthropology, Cultural":"GEN",
    "Anthropology, Medical and Forensic":"GEN",
    "Anthropology, Physical":"GEN",
    "Applied Mathematics":"PHY",
    "Applied Mechanics":"PHY",
    "Architecture":"GEN",
    "Area Planning and Development":"GEN",
    "Art History":"GEN",
    "Artificial Intelligence":"GEN",
    "Atmospheric Chemistry":"PHY",
    "Atmospheric Sciences":"PHY",
    "Biogeochemistry":"GEN",
    "Biography":"GEN",
    "Biology, Anatomy":"GEN",
    "Biology, Animal Physiology":"GEN",
    "Biology, Bioinformatics":"GEN",
    "Biology, Biostatistics":"GEN",
    "Biology, Botany":"GEN",
    "Biology, Cell":"GEN",
    "Biology, Conservation":"GEN",
    "Biology, Ecology":"GEN",
    "Biology, Entomology":"GEN",
    "Biology, General":"GEN",
    "Biology, Genetics":"GEN",
    "Biology, Landscape Ecology":"GEN",
    "Biology, Limnology":"GEN",
    "Biology, Microbiology":"GEN",
    "Biology, Molecular":"GEN",
    "Biology, Neurobiology":"GEN",
    "Biology, Neuroscience":"GEN",
    "Biology, Oceanography":"GEN",
    "Biology, Physiology":"GEN",
    "Biology, Plant Physiology":"GEN",
    "Biology, Virology":"GEN",
    "Biology, Zoology":"GEN",
    "Biophysics, Biomechanics":"PHY",
    "Biophysics, General":"PHY",
    "Biophysics, Medical":"PHY",
    "Black Studies":"GEN",
    "Business Administration, Accounting":"GEN",
    "Business Administration, Banking":"GEN",
    "Business Administration, Entrepreneurship":"GEN",
    "Business Administration, General":"GEN",
    "Business Administration, Management":"GEN",
    "Business Administration, Marketing":"GEN",
    "Canadian Studies":"GEN",
    "Chemical Oceanography":"PHY",
    "Chemistry, Agricultural":"GEN",
    "Chemistry, Analytical":"GEN",
    "Chemistry, Biochemistry":"GEN",
    "Chemistry, General":"GEN",
    "Chemistry, Inorganic":"GEN",
    "Chemistry, Molecular":"GEN",
    "Chemistry, Nuclear":"GEN",
    "Chemistry, Organic":"GEN",
    "Chemistry, Pharmaceutical":"GEN",
    "Chemistry, Physical":"GEN",
    "Chemistry, Polymer":"GEN",
    "Chemistry, Radiation":"GEN",
    "Cinema":"GEN",
    "Climate Change":"PHY",
    "Computer Science":"GEN",
    "Continental Dynamics":"PHY",
    "Cultural Resources Management":"GEN",
    "Design and Decorative Arts":"GEN",
    "Economics, Agricultural":"GEN",
    "Economics, Commerce-Business":"GEN",
    "Economics, Environmental":"GEN",
    "Economics, Finance":"GEN",
    "Economics, General":"GEN",
    "Economics, History":"GEN",
    "Economics, Labor":"GEN",
    "Economics, Theory":"GEN",
    "Education, Administration":"EDU",
    "Education, Adult and Continuing":"EDU",
    "Education, Agricultural":"EDU",
    "Education, Art":"EDU",
    "Education, Bilingual and Multicultural":"EDU",
    "Education, Business":"EDU",
    "Education, Community College":"EDU",
    "Education, Continuing":"EDU",
    "Education, Curriculum and Instruction":"EDU",
    "Education, Early Childhood":"EDU",
    "Education, Educational Psychology":"EDU",
    "Education, Elementary":"EDU",
    "Education, English as a Second Language":"EDU",
    "Education, Environmental":"EDU",
    "Education, Evaluation":"EDU",
    "Education, Finance":"EDU",
    "Education, General":"EDU",
    "Education, Gifted":"EDU",
    "Education, Guidance and Counseling":"EDU",
    "Education, Health":"EDU",
    "Education, Higher":"EDU",
    "Education, History of":"EDU",
    "Education, Industrial":"EDU",
    "Education, Instructional Design":"EDU",
    "Education, Language and Literature":"EDU",
    "Education, Leadership":"EDU",
    "Education, Mathematics":"EDU",
    "Education, Middle School":"EDU",
    "Education, Multilingual":"EDU",
    "Education, Music":"EDU",
    "Education, Pedagogy":"EDU",
    "Education, Philosophy of":"EDU",
    "Education, Physical":"EDU",
    "Education, Policy":"EDU",
    "Education, Reading":"EDU",
    "Education, Religious":"EDU",
    "Education, Sciences":"EDU",
    "Education, Secondary":"EDU",
    "Education, Social Sciences":"EDU",
    "Education, Sociology of":"EDU",
    "Education, Special":"EDU",
    "Education, Teacher Training":"EDU",
    "Education, Technology of":"EDU",
    "Education, Tests and Measurements":"EDU",
    "Education, Vocational":"EDU",
    "Energy":"PHY",
    "Engineering, Aerospace":"PHY",
    "Engineering, Agricultural":"PHY",
    "Engineering, Architectural":"PHY",
    "Engineering, Automotive":"PHY",
    "Engineering, Biomedical":"PHY",
    "Engineering, Chemical":"PHY",
    "Engineering, Computer":"GEN",
    "Engineering, Civil":"PHY",
    "Engineering, Electronics and Electrical":"PHY",
    "Engineering, Environmental":"PHY",
    "Engineering, General":"PHY",
    "Engineering, Geological":"PHY",
    "Engineering, Geophysical":"PHY",
    "Engineering, Industrial":"PHY",
    "Engineering, Marine and Ocean":"PHY",
    "Engineering, Materials Science":"PHY",
    "Engineering, Mechanical":"PHY",
    "Engineering, Metallurgy":"PHY",
    "Engineering, Mining":"PHY",
    "Engineering, Naval":"PHY",
    "Engineering, Nuclear":"PHY",
    "Engineering, Packaging":"PHY",
    "Engineering, Petroleum":"PHY",
    "Engineering, Robotics":"PHY",
    "Engineering, Sanitary and Municipal":"PHY",
    "Engineering, System Science":"PHY",
    "Environmental Health":"GEN",
    "Environmental Law":"GEN",
    "Environmental Management":"GEN",
    "Environmental Sciences":"PHY",
    "Environmental Studies":"GEN",
    "Ethics":"GEN",
    "Fine Arts":"GEN",
    "Gender Studies":"GEN",
    "Geobiology":"PHY",
    "Geochemistry":"PHY",
    "Geodesy":"PHY",
    "Geography":"PHY",
    "Geological Survey":"PHY",
    "Geology":"PHY",
    "Geomorphology":"PHY",
    "Geophysics":"PHY",
    "Geotechnology":"PHY",
    "Gerontology":"GEN",
    "GLBT Studies":"GEN",
    "Health Sciences, Audiology":"GEN",
    "Health Sciences, Dentistry":"GEN",
    "Health Sciences, Education":"EDU",
    "Health Sciences, Epidemiology":"GEN",
    "Health Sciences, General":"GEN",
    "Health Sciences, Human Development":"GEN",
    "Health Sciences, Immunology":"GEN",
    "Health Sciences, Medicine and Surgery":"GEN",
    "Health Sciences, Nursing":"GEN",
    "Health Sciences, Nutrition":"GEN",
    "Health Sciences, Obstetrics and Gynecology":"GEN",
    "Health Sciences, Occupational Health and Safety":"GEN",
    "Health Sciences, Oncology":"GEN",
    "Health Sciences, Ophthalmology":"GEN",
    "Health Sciences, Pathology":"GEN",
    "Health Sciences, Pharmacology":"GEN",
    "Health Sciences, Pharmacy":"GEN",
    "Health Sciences, Public Health":"GEN",
    "Health Sciences, Radiology":"GEN",
    "Health Sciences, Recreation":"GEN",
    "Health Sciences, Rehabilitation and Therapy":"GEN",
    "Health Sciences, Speech Pathology":"GEN",
    "Health Sciences, Surgery":"GEN",
    "Health Sciences, Toxicology":"GEN",
    "Hispanic American Studies":"GEN",
    "History of Science":"GEN",
    "History, African":"GEN",
    "History, Ancient":"GEN",
    "History, Asia, Australia and Oceania":"GEN",
    "History, Black":"GEN",
    "History, Canadian":"GEN",
    "History, European":"GEN",
    "History, Latin American":"GEN",
    "History, Medieval":"GEN",
    "History, Modern":"GEN",
    "History, United States":"GEN",
    "Home Economics":"GEN",
    "Hydrology":"PHY",
    "Information Science":"GEN",
    "Information Technology":"GEN",
    "Journalism":"GEN",
    "Land Use Planning":"GEN",
    "Landscape Architecture":"GEN",
    "Language, General":"GEN",
    "Language, Linguistics":"GEN",
    "Language, Modern":"GEN",
    "Language, Rhetoric and Composition":"GEN",
    "Latin American Studies":"GEN",
    "Law":"GEN",
    "Library Science":"GEN",
    "Literature, American":"GEN",
    "Literature, Classical":"GEN",
    "Literature, English":"GEN",
    "Literature, Modern":"GEN",
    "Marine Geology":"PHY",
    "Mass Communications":"GEN",
    "Mathematics":"PHY",
    "Meteorology":"PHY",
    "Military Studies":"GEN",
    "Mineralogy":"PHY",
    "Museology":"GEN",
    "Music":"GEN",
    "Nanoscience":"PHY",
    "Nanotechnology":"PHY",
    "Native American Studies":"GEN",
    "Natural Resource Management":"GEN",
    "Operations Research":"GEN",
    "Paleobotany":"PHY",
    "Paleoclimate Science":"GEN",
    "Paleoecology":"PHY",
    "Paleontology":"PHY",
    "Palynology":"PHY",
    "Petroleum Geology":"PHY",
    "Petrology":"PHY",
    "Philosophy":"GEN",
    "Philosophy of Science":"GEN",
    "Physical Geography":"PHY",
    "Physical Oceanography":"PHY",
    "Physics, Acoustics":"PHY",
    "Physics, Astronomy and Astrophysics":"AST",
    "Physics, Astrophysics":"AST",
    "Physics, Atmospheric Science":"PHY",
    "Physics, Atomic":"PHY",
    "Physics, Condensed Matter":"PHY",
    "Physics, Electricity and Magnetism":"PHY",
    "Physics, Elementary Particles and High Energy":"PHY",
    "Physics, Fluid and Plasma":"PHY",
    "Physics, General":"PHY",
    "Physics, High Temperature":"PHY",
    "Physics, Low Temperature":"PHY",
    "Physics, Molecular":"PHY",
    "Physics, Nuclear":"PHY",
    "Physics, Optics":"PHY",
    "Physics, Quantum":"PHY",
    "Physics, Radiation":"PHY",
    "Physics, Solid State":"PHY",
    "Physics, Theory":"PHY",
    "Planetology":"AST",
    "Plastics Technology":"PHY",
    "Plate Tectonics":"PHY",
    "Political Science, General":"GEN",
    "Political Science, International Law and Relations":"GEN",
    "Political Science, International Relations":"GEN",
    "Political Science, Public Administration":"GEN",
    "Psychology, Behavioral":"GEN",
    "Psychology, Clinical":"GEN",
    "Psychology, Cognitive":"GEN",
    "Psychology, Counseling":"GEN",
    "Psychology, Developmental":"GEN",
    "Psychology, Experimental":"GEN",
    "Psychology, General":"GEN",
    "Psychology, Industrial":"GEN",
    "Psychology, Personality":"GEN",
    "Psychology, Physiological":"GEN",
    "Psychology, Psychobiology":"GEN",
    "Psychology, Psychometrics":"GEN",
    "Psychology, Social":"GEN",
    "Recreation":"GEN",
    "Religion, Biblical Studies":"GEN",
    "Religion, General":"GEN",
    "Religion, History of":"GEN",
    "Religion, Philosophy of":"GEN",
    "Remote Sensing":"PHY",
    "Sedimentary Geology":"PHY",
    "Social Work":"GEN",
    "Sociology, Criminology and Penology":"GEN",
    "Sociology, Demography":"GEN",
    "Sociology, Environmental Justice":"GEN",
    "Sociology, Ethnic and Racial Studies":"GEN",
    "Sociology, General":"GEN",
    "Sociology, Individual and Family Studies":"GEN",
    "Sociology, Industrial and Labor Relations":"GEN",
    "Sociology, Organizational":"GEN",
    "Sociology, Public and Social Welfare":"GEN",
    "Sociology, Social Structure and Development":"GEN",
    "Sociology, Sociolinguistics":"GEN",
    "Sociology, Theory and Methods":"GEN",
    "Speech Communication":"GEN",
    "Statistics":"GEN",
    "Sub Saharan Africa Studies":"GEN",
    "Sustainability":"GEN",
    "Textile Technology":"GEN",
    "Theater":"GEN",
    "Theology":"GEN",
    "Theoretical Mathematics":"PHY",
    "Transportation":"GEN",
    "Urban and Regional Planning":"GEN",
    "Water Resource Management":"PHY",
    "Web Studies":"GEN",
    "Women's Studies":"GEN",
    }
