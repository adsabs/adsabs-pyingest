from __future__ import absolute_import, unicode_literals
import adsdata.app as app_module
from adsputils import get_date, exceptions
from kombu import Queue
import os
from adsmsg import BibRecord

# ============================= INITIALIZATION ==================================== #

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
app = app_module.AdsArxivCelery('ads-arxiv', proj_home=proj_home)
logger = app.logger


app.conf.CELERY_QUEUES = (
    Queue('output-results', app.exchange, routing_key='output-results'),
)


# ============================= TASKS ============================================= #


@app.task(queue='output-results')
def task_output_results(msg):
    """
    This worker will forward results to the outside
    exchange (typically an ADSMasterPipeline) to be
    incorporated into the storage
    :param msg: a protobuf containing the non-bibliographic metadata
            {'bibcode': '....',
             'reads': [....],
             'simbad': '.....',
             .....
            }
    :return: no return
    """
    logger.debug('Will forward this nonbib record: %s', msg)
    app.forward_message(msg)


if __name__ == '__main__':
    app.start()
