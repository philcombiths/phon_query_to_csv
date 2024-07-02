"""
Logging configuration
"""

import logging
from sys import stdout

def setup_logging(loglevel, logfile='csv_compiler_errors.txt'):
    """Setup basic logging for script execution

    Args:
      loglevel (int): minimum loglevel for emitting messages
      logfile (str): log file to save messages to

    Raises:
      ValueError: if loglevel is not a valid logging level
      FileNotFoundError: if log file cannot be opened
    """
    # Check if loglevel is valid
    if not isinstance(loglevel, int) or not 0 <= loglevel <= logging.DEBUG:
        raise ValueError("loglevel must be an integer between 0 and {}".format(logging.DEBUG))

    # Set up logging format
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Get logger instance
    log = logging.getLogger(__name__)

    # Set up formatter
    formatter = logging.Formatter("%(message)s - %(levelname)s - %(asctime)s")
    formatter2 = logging.Formatter("%(message)s")

    # Clear existing handlers
    if log.hasHandlers():
        log.handlers.clear()

    try:
        # Set up file handler
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter2)

        # Set up console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        # Add handlers to logger
        log.addHandler(fh)
        log.addHandler(ch)
    except IOError as e:
        raise FileNotFoundError("Error opening log file: {}".format(e))

    return log
        
