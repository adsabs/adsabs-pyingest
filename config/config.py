#!/usr/bin/env python

INCOMING_ABS_DIR = '/proj/ads/abstracts/sources/ArXiv'

UPDATE_AGENT_DIR = INCOMING_ABS_DIR + '/UpdateAgent'

ARCHIVE_ABS_DIR = INCOMING_ABS_DIR + '/oai/arXiv.org'


# ================= celery/rabbitmq rules============== #
# ##################################################### #

ACKS_LATE=True
PREFETCH_MULTIPLIER=1
CELERYD_TASK_SOFT_TIME_LIMIT = 60

CELERY_DEFAULT_EXCHANGE = 'ads-arxiv'
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"

CELERY_BROKER = 'pyamqp://guest:guest@localhost:5682/arxiv_pipeline'
OUTPUT_CELERY_BROKER = 'pyamqp://guest:guest@localhost:5682/master_pipeline'
OUTPUT_TASKNAME = 'adsmp.tasks.task_update_record'
