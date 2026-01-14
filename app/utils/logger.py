import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "instance"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Pastikan folder instance ada
os.makedirs(LOG_DIR, exist_ok=True)

log_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=1_000_000, backupCount=3
)

log_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

log_handler.setFormatter(log_formatter)

logger = logging.getLogger("DicomGateway")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
