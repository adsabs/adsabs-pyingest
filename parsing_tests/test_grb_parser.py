from glob import glob
from pyingest.parsers.gcncirc import GCNCParser

PATH = '/Users/mtempleton/gcn3/'

gcn_files = glob(PATH + '*.gcn3')
gcn_files.sort()

gcn_files = gcn_files[500:510]
#gcn_files = ['/Users/mtempleton/gcn3/12476.gcn3']

for f in gcn_files:
    with open(f,'rU') as fg:
        fdata = fg.read()
        gcnc = GCNCParser(fdata)
        out = gcnc.parse()
        print f
        print out['author']
#       try:
#           del(out['raw'])
#       except:
#           print "\n\nERROR: %s\n\n" % out['error']
