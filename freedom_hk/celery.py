import os
from celery import Celery
from celery.signals import after_setup_logger, worker_shutting_down
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freedom_hk.settings')

app = Celery('freedom_hk')
app.config_from_object('freedom_hk.celery_config')
app.autodiscover_tasks()

@worker_shutting_down.connect
def worker_shutting_down_handler(sig, how, exitcode, **kwargs):
    logger.info('Worker shutting down...')

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    fh = logging.FileHandler('celery.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)