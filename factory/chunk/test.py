from util.pylogger import LogUtility

def test():
    logger = LogUtility.get_logger("chunk")

    logger.debug("test")