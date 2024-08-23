from celery import Celery
from celery.schedules import crontab

app = Celery('aban_tether')

app.conf.beat_schedule = {
    'AGGREGATE_AND_BUY_FROM_EXCHANGE': {
        'task': 'exchange.tasks.aggregate_and_buy_from_exchange',
        'schedule': crontab(minute='*/1'),  # Runs every minute
    },
}
