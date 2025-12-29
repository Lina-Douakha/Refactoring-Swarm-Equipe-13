
import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    '''Configure un logger pour le projet'''
    logger = logging.getLogger(name)
    
    # Éviter de dupliquer les handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Handler console
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger