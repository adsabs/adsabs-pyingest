from __future__ import absolute_import, unicode_literals
#from aip import app as app_module
#from aip.libs import solr_adapter, merger, read_records
#from kombu import Queue
#from adsmsg import BibRecord, DenormalizedRecord

#app = app_module.ADSImportPipelineCelery('import-pipeline')
#logger = app.logger

class ArxivToMasterPipeline(dict):

    def serialize(self, record, **kwargs):

        if (len(record.keys()) > 0):
            print ("Sending to master pipeline, jk lol....")
#           print (record)
        else:
            print ("Null record, not sending to master pipeline")
