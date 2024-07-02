"""
Logging configuration
"""

import logging

def setup_logging(loglevel,file_name, logfile='phon_query_to_csv.log'):
    """Setup basic logging for script execution

    Args:
      loglevel (int): minimum loglevel for emitting messages
      logfile (str): log file to save messages to
    """

    logger = logging.getLogger(file_name)
    logger.propagate = False # Prevents duplicate logging to console
    logger.setLevel(loglevel)

    # create console handler and set    level to debug
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    ch.setFormatter(logging.Formatter('%(message)s'))

    # create file handler and set level to debug
    fh = logging.FileHandler(logfile)
    fh.setLevel(loglevel)
    fh.setFormatter(logging.Formatter('%(message)s | %(asctime)s | %(levelname)s | %(name)s '))

    # add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
        
