from __future__ import absolute_import, unicode_literals

#import ADSPipeline

#from aip import app as app_module
#from aip.libs import solr_adapter, merger, read_records
#from kombu import Queue
#from adsmsg import BibRecord, DenormalizedRecord

#app = app_module.ADSImportPipelineCelery('import-pipeline')
#logger = app.logger

from adsarxiv.tasks import task_output_results

class ArxivToMasterPipeline(dict):

    def serialize(self, record, **kwargs):

        if (len(record.keys()) > 0):
#           print ("Sending to master pipeline, jk lol....")
#           print (record)
            rec = BibRecord(**record)
            task_output_results.delay(rec)
        else:
            print ("Null record, not sending to master pipeline")
