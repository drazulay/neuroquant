import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def timestamp():
    return int(time.time() * 1000)
