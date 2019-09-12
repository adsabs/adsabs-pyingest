import os
from pyingest.config.config import *

class WriteErrorException(Exception):
    pass

class NoReferencesException(Exception):
    pass

class ReferenceWriter(object):

    def __init__(self):
        self.topdir = REFERENCE_TOPDIR
        self.refsource = ''


    def writeref(self, output_metadata):
        if isinstance(output_metadata,dict):
            try:
                output_metadata['refhandler_list']
            except Exception, err:
                raise NoReferencesException(err)
            else:
                try:
                    # you need this info to write files
                    # if any arent available, generate exception
                    bibcode = output_metadata['bibcode']
                    bibstem = bibcode[4:9].rstrip('.')
                    volume = str(output_metadata['volume']).rjust(4,'0')
                    file_ext = self.refsource
                    reflist = output_metadata['refhandler_list']

                    outdir = self.topdir + bibstem + '/' + volume
                    outfile = outdir + '/' + bibcode + file_ext

                    if not os.path.isdir(outdir):
                        os.makedirs(outdir)
                    with open(outfile, 'w') as fw:
                        fw.write("<ADSBIBCODE>%s</ADSBIBCODE>\n" % bibcode)
                        for s in reflist:
                            fw.write(s.encode('utf8')+'\n')
                except Exception, err:
                    raise WriteErrorException(err)
        return
