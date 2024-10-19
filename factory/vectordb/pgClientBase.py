from util.pylogger import LogUtility
import psycopg, sys

class PgClientBaseClass:
    def __init__(self, config):
        self.config = config

        try:
            self.logger = LogUtility.get_logger(__name__)

            #connectionStr = f"postgresql://{config.PG_USER}:{config.PG_PWD}@{config.PG_OHST}:{config.PG_PORT}/{config.PG_DBNAME}"  
            self.conn = psycopg.connect(
                user=config.PG_USER,
                password=config.PG_PWD,
                host=config.PG_HOST,
                port=config.PG_PORT,
                dbname=config.PG_DBNAME, autocommit=True)

        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise
   
