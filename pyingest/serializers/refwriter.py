import os
import sys

from adsputils import load_config

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__),'../../'))
conf = load_config(proj_home=proj_home)

if sys.version_info > (3,):
    str_type = str
else:
    str_type = unicode


class WriteErrorException(Exception):
    pass


class NoReferencesException(Exception):
    pass


class ReferenceWriter(object):

    def __init__(self):
        self.topdir = conf.get('REFERENCE_TOPDIR', './')
        self.refsource = conf.get('REFSOURCE_DICT', {})

    def writeref(self, output_metadata, source='iop'):
        if isinstance(output_metadata, dict):
            try:
                output_metadata['refhandler_list']
            except Exception as err:
                pass
                # raise NoReferencesException(err)
            else:
                try:
                    # you need this info to write files
                    # if any arent available, generate exception
                    bibcode = output_metadata['bibcode']
                    bibstem = bibcode[4:9].rstrip('.')
                    volume = str_type(output_metadata['volume']).rjust(4, '0')
                    file_ext = self.refsource[source]
                    reflist = output_metadata['refhandler_list']

                    outdir = self.topdir + bibstem + '/' + volume
                    outfile = outdir + '/' + bibcode + "." + file_ext

                    if not os.path.isdir(outdir):
                        os.makedirs(outdir)
                    with open(outfile, 'w') as fw:
                        fw.write("<ADSBIBCODE>%s</ADSBIBCODE>\n" % bibcode)
                        for s in reflist:
                            fw.write(str_type(s) + '\n')
                except Exception as err:
                    print("exception in writeref:",err)
                    # pass
                    # raise WriteErrorException(err)
        return
