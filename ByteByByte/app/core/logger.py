# logger.py
import logging
import os
from app.core.config import LOGS_DIR

def get_logger(name):
    """Возвращает логгер с записью в файл и консоль"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, "app.log")
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Если обработчики уже есть, не добавляем повторно
    if logger.handlers:
        return logger
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
