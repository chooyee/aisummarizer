import os,sys
from supabase import create_client, Client
from supabase.client import ClientOptions
from util.pylogger import LogUtility

class Supaclient:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def __enter__(self):
        config = self.config
        try:
            self.logger = LogUtility.get_logger(__name__)

            url: str = config.SUPABASE_URL
            key: str = config.SUPABASE_KEY
            self.supabase: Client = create_client(url, key,
                options=ClientOptions(
                    postgrest_client_timeout=10,
                    storage_client_timeout=10,
                    schema="public",
            ))
            response = self.supabase.auth.sign_in_with_password({
                "email": config.SUPABASE_USER,
                "password": config.SUPABASE_PWD
            })
            return self.supabase
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        self.supabase.auth.sign_out()

