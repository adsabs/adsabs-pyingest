#!/usr/bin/env python

from pyingest.parsers.iop import IOPJATSParser
from pyingest.serializers.classic import Tagged
from pyingest.serializers.refwriter import ReferenceWriter
from glob import glob
import subprocess
import argparse

# This calls for latest volume/issue which isn't going to work when we need to span volumes
#
#for issn in journal_ISSN.keys():
#    b2 = basedir+issn
#    vols = glob(b2+'/*')
#    v = vols[-1]
#    iss = glob(v+'/*')
#    i = iss[-1]
#    papers = glob(i+'/*/*.xml')
#
# Instead, we want to have arguments:
#  -j journal
#  -v volume
#  -i issue
# 
# or call with database and "since last" with a timestamp
#  -n last n days
#  -d database
#

ASTjournal_ISSN = {
                'AJ': '1538-3881',
                'JCAP': '1475-7516',
                'ApJ': '0004-637X',
                'ApJS': '0067-0049',
                'PASP': '1538-3873',
                'ApJL': '2041-8205',
                'PSJ': '2632-3338',
                'RAA': '1674-4527',
                'RNAAS': '2515-5172'
               }
basedir = '/proj/ads/articles/sources/STACKS/'

PHYjournal_ISSN = {
                'ANSNN': '2043-6262',
                'APExp': '1882-0786',
                'CQGra': '0264-9381',
                'ChPhB': '1674-1056',
                'ChPhC': '1674-1137',
                'ChPhL': '0256-307X',
                'CoTPh': '0253-6102',
                'E&ES': '1755-1315',
                'ECSIn': '1064-8208',
                'ECSMA': '2151-2043',
                'ECSTr': '1938-5862',
                'EJPh': '0143-0807',
                'EL': '0295-5075',
                'ERCom': '2515-7620',
                'ERExp': '2631-8695',
                'ERL': '1748-9326',
                'EleSt': '2516-1075',
                'FCS': '2631-6331',
                'FlDyR': '1873-7005',
                'InvPr': '0266-5611',
                'IzMat': '1064-5632',
                'JGE': '1742-2140',
                'JInst': '1748-0221',
                'JMiMi': '0960-1317',
                'JNEng': '1741-2552',
                'JOpt': '2040-8986',
                'JPCM': '0953-8984',
                'JPEn': '2515-7655',
                'JPhA': '1751-8121',
                'JPhB': '0953-4075',
                'JPhC': '0022-3719',
                'JPhCS': '1742-6596',
                'JPhCo': '2399-6528',
                'JPhD': '0022-3727',
                'JPhF': '0305-4608',
                'JPhG': '0954-3899',
                'JPhM': '2515-7639',
                'JPhP': '2515-7647',
                'JPhy2': '0022-3700',
                'JElS': '0013-4651',
                'JSMTE': '1742-5468',
                'JSemi': '1674-4926',
                'JSSST': '2162-8769',
                'JaJAP': '1347-4065',
                'LaPhL': '1612-202X',
                'LaPhy': '1555-6611',
                'MApFl': '2050-6120',
                'MRE': '2053-1591',
                'MS&E': '1757-899X',
                'MSMSE': '0965-0393',
                'MeScT': '0957-0233',
                'Metro': '0026-1394',
                'MuMat': '2399-7532',
                'NJPh': '1367-2630',
                'NanoE': '2632-959X',
                'NanoF': '2399-1984',
                'Nanot': '0957-4484',
                'Nonli': '0951-7715',
                'NucFu': '0029-5515',
                'PMB': '0031-9155',
                'PPCF': '0741-3335',
                'PPS': '0370-1328',
                'PRCom': '2516-1067',
                'PSST': '0963-0252',
                'PhyEd': '0031-9120',
                'PhyS': '1402-4896',
                'PhyU': '1063-7869',
                'PhyW': '2058-7058',
                'PlST': '1009-0630',
                'PrEne': '2516-1083',
                'QS&T': '2058-9565',
                'QuEle': '1063-7818',
                'RPPh': '0034-4885',
                'RuCRv': '0036-021X',
                'RuMaS': '0036-0279',
                'SMaS': '0964-1726',
                'SbMat': '1064-5616',
                'SeScT': '0268-1242',
                'SuScT': '0953-2048',
                'SuTMP': '2051-672X',
                'TDM': '2053-1583'
               }



def parse_arguments():
    """
    returns an argparse.ArgumentParser().parse_args() object
    """
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '-j',
        '--journal',
        type=str,
        help='specifies journal bibstem to process'
        )
    argp.add_argument(
        '-v',
        '--volume',
        type=str,
        help='specifies volume to process'
        )
    argp.add_argument(
        '-i',
        '--issue',
        type=str,
        help='specifies issue number to process'
				)
    argp.add_argument(
        '-n',
        '--numdays',
        type=int,
        help='specifies number of days to process'
				)
    argp.add_argument(
        '-d',
        '--database',
        type=str,
        help='specifies which database to process'
				)
#   argp.add_argument('files', nargs='+')
    return argp.parse_args()


outfile = 'iop_test.tag'

# use: ASTjournal_ISSN[argp.journal]

parser = IOPJATSParser()

if __name__ == "__main__":

    args = parse_arguments()
    if args.issue:
        issue = args.issue
    else:
        issue = '*'
#   print "issue",args.issue

    if args.volume:
        volume = args.volume
    else:
        volume = '*'
#   print "volume",args.volume

    if args.journal:
        try:
            issn = ASTjournal_ISSN[args.journal]
        except Exception as e:
            print("Warning: No AST ISSN for:",args.journal)
        try:
            issn = PHYjournal_ISSN[args.journal]
        except Exception as e:
            print("Warning: No PHY ISSN for:",args.journal)
#   elif args.numdays:
#       numdays = args.numdays
#       print "since last",args.numdays
#       try:
#           database = args.database
#       except Exception as e:
#           print("Need to specify database for:",args.numdays)
    else:
        print "Journal required"
        exit(0)
#   print "journal",args.journal
#   print "PHYjournal_ISSN[args.journal]"
#   print "issn",issn

#   subprocess.call(["ls", "-l"])
    path = basedir+issn+'/'+volume+'/'+issue
#   print "path",path
    files = glob(path+'/*/*[0-9].xml')

    documents = []
    for f in files:
#       print(f)
        try:
            with open(f, 'rU') as fp:
                doc = parser.parse(fp)
                documents.append(doc)
        except Exception as e:
            print("Error in IOP parser:", f, e)

# Write everything out in Classic tagged format
    fo = open(outfile, 'a')

    serializer = Tagged()
    ref_handler = ReferenceWriter()

#   documents = documents[0:]
    for d in documents:
#       print(d)
        serializer.write(d, fo)
        ref_handler.writeref(d)
    fo.close()


