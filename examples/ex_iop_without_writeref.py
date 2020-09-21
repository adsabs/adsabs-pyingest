#!/usr/bin/env python

from __future__ import print_function
from pyingest.parsers.iop import IOPJATSParser
from pyingest.serializers.classic import Tagged
from glob import glob
import os
import json


outfile = 'iop_test.tag'

'''
journal_ISSN = {
    '1538-3881': 'AJ',
    '2043-6262': 'ANSNN',
    '1882-0786': 'APExp',
    '0004-637X': 'ApJ',
    '2041-8205': 'ApJ',
    '2041-8205': 'ApJL',
    '0067-0049': 'ApJS',
    '1748-3190': 'BiBi',
    '1758-5090': 'BioFa',
    '1748-605X': 'BioMa',
    '0264-9381': 'CQGra',
    '1009-9271': 'ChJAA',
    '1674-1056': 'ChPhB',
    '1674-1137': 'ChPhC',
    '0256-307X': 'ChPhL',
    '0253-6102': 'CoTPh',
    '1755-1315': 'E&ES',
    '0143-0807': 'EJPh',
    '0295-5075': 'EL',
    '2515-7620': 'ERCom',
    '2631-8695': 'ERExp',
    '1748-9326': 'ERL',
    '2516-1075': 'EleSt',
    '2631-6331': 'FCS',
    '1873-7005': 'FlDyR',
    '0266-5611': 'InvPr',
    '1064-5632': 'IzMat',
    '1752-7163': 'JBR',
    '1475-7516': 'JCAP',
    '1742-2140': 'JGE',
    '1748-0221': 'JInst',
    '0960-1317': 'JMiMi',
    '1741-2552': 'JNEng',
    '2040-8986': 'JOpt',
    '0953-8984': 'JPCM',
    '2515-7655': 'JPEn',
    '0305-4470': 'JPhA',
    '1751-8121': 'JPhA',
    '0953-4075': 'JPhB',
    '1742-6596': 'JPhCS',
    '2399-6528': 'JPhCo',
    '0022-3727': 'JPhD',
    '0954-3899': 'JPhG',
    '2515-7639': 'JPhM',
    '2515-7647': 'JPhP',
    '0952-4746': 'JRP',
    '1742-5468': 'JSMTE',
    '1674-4926': 'JSemi',
    '1347-4065': 'JaJAP',
    '1612-202X': 'LaPhL',
    '1555-6611': 'LaPhy',
    '2050-6120': 'MApFl',
    '2053-1591': 'MRE',
    '1757-899X': 'MS&E',
    '0965-0393': 'MSMSE',
    '0957-0233': 'MeScT',
    '0026-1394': 'Metro',
    '2399-7532': 'MuMat',
    '1367-2630': 'NJPh',
    '2399-1984': 'NanoF',
    '0957-4484': 'Nanot',
    '0951-7715': 'Nonli',
    '0029-5515': 'NucFu',
    '1538-3873': 'PASP',
    '0031-9155': 'PMB',
    '0741-3335': 'PPCF',
    '0370-1328': 'PPS',
    '2516-1067': 'PRCom',
    '0963-0252': 'PSST',
    '1478-3975': 'PhBio',
    '1402-4896': 'PhST',
    '0031-9120': 'PhyEd',
    '0967-3334': 'PhyM',
    '1402-4896': 'PhyS',
    '1063-7869': 'PhyU',
    '1009-0630': 'PlST',
    '2516-1083': 'PrEne',
    '2058-9565': 'QS&T',
    '1063-7818': 'QuEle',
    '1674-4527': 'RAA',
    '2515-5172': 'RNAAS',
    '0034-4885': 'RPPh',
    '0036-021X': 'RuCRv',
    '0036-0279': 'RuMaS',
    '0964-1726': 'SMaS',
    '1064-5616': 'SbMat',
    '0268-1242': 'SeScT',
    '0953-2048': 'SuScT',
    '2051-672X': 'SuTMP',
    '2053-1583': 'TDM'
}
'''
journal_ISSN = {
    #'1538-3881': 'AJ',
    '0004-637X': 'ApJ',
    #'1402-4896': 'PhST',
    '0031-9120': 'PhyEd',
    #'0967-3334': 'PhyM',
    '1402-4896': 'PhyS',
    #'1063-7869': 'PhyU',
    '1009-0630': 'PlST',
    #'2516-1083': 'PrEne',
    '2058-9565': 'QS&T',
    #'1063-7818': 'QuEle',
    '1674-4527': 'RAA',
    '2515-5172': 'RNAAS',
    '0034-4885': 'RPPh'
}

parser = IOPJATSParser()


basedir = '/proj/ads/articles/sources/STACKS/'

issn_list = journal_ISSN.keys()
issn_list.sort()

for issn in issn_list:
    b2 = basedir + issn
    vols = glob(b2 + '/*')
    vols.sort(key=os.path.getmtime)
    v = vols[-1]
    papers = glob(v + '/*/*/*.xml')
    papers2 = []
    for p in papers:
        if 'refs.xml' not in p and 'meta.xml' not in p:
            papers2.append(p)

    papers = papers2

    # Try the parser
    documents = []
    for p in papers:
        try:
            with open(p, 'rU') as fp:
                doc = parser.parse(fp)
                if doc != {}:
                    documents.append(doc)
        except Exception as e:
            print("Error in IOP parser:", p, e)

    # Write everything out in Classic tagged format
    fo = open(outfile, 'a')

    serializer = Tagged()

    for d in documents:
        if 'bibcode' in d:
            if 'XSTEM' in d['bibcode']:
                print("Bad bibcode:", d['bibcode'])
        else:
            print("no bibcode...")
        serializer.write(d, fo)
    fo.close()
