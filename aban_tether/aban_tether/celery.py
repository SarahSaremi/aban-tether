from celery import Celery
from celery.schedules import crontab

app = Celery('order_system')

app.conf.beat_schedule = {
    'aggregate-and-buy-every-minute': {
        'task': 'orders.tasks.aggregate_and_buy_from_exchange',
        'schedule': crontab(minute='*/1'),  # Runs every minute
    },
}
