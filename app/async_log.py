import asyncio
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import QueueHandler
from logging.handlers import QueueListener
from logging import StreamHandler
from queue import Queue

LOGS_DIR = 'logs/'
APP_NAME = 'dimatech_web'
NOW_DATETIME = datetime.datetime.now() + datetime.timedelta(hours=3)
NOW_DATE_STR_FILE = NOW_DATETIME.strftime('%Y%m%d')



async def init_logger():
    """Логгер."""
    log = logging.getLogger()
    que = Queue()
    log.addHandler(QueueHandler(que))
    
    handler = TimedRotatingFileHandler(
        filename=f'{LOGS_DIR}{APP_NAME}_{NOW_DATE_STR_FILE}.log', 
        when='midnight', 
        interval=1, 
        backupCount=7,  # Хранить 7 предыдущих файлов
        encoding='utf-8'
    )
    log.addHandler(handler)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(message)s',
        filemode='a',
    )
    
    log.setLevel(logging.INFO)
    listener = QueueListener(que, StreamHandler())
    try:
        listener.start()
        logging.debug('Logger has started')
        while True:
            await asyncio.sleep(10)
    finally:
        logging.debug('Logger is shutting down')
        listener.stop()