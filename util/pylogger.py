import logging
from logging.handlers import TimedRotatingFileHandler
import os

class LogUtility:
    _logger = None

    @staticmethod
    def get_logger(sysname):
        if LogUtility._logger is None:
            # Create a custom logger
            logger = logging.getLogger(sysname)
            # Set logging level based on environment variable
            log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
            logger.setLevel(getattr(logging, log_level, logging.INFO))

            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            logger.addHandler(ch)

            # Create a handler that writes log messages to a file, rotating the log file every day
            logPath = "./log"
            if not os.path.exists(logPath):
                os.makedirs(logPath)
            handler = TimedRotatingFileHandler(f'{logPath}/log.log', when='midnight', interval=1)
            handler.suffix = "%Y-%m-%d"  # This will add the date to the log file name

            # Create a formatter and set it for the handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            # Add the handler to the logger
            logger.addHandler(handler)

            LogUtility._logger = logger

        return LogUtility._logger
