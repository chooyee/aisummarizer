import configparser
from os import environ as env
from dotenv import load_dotenv

class GlobalConfig(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            load_dotenv()
            cls.instance = super(GlobalConfig, cls).__new__(cls)
           
            systemEnv = env["system_env"]          
            config = configparser.ConfigParser()
            config.sections()
            config.read('config.cfg')
            # cls.instance.CLIENT_ID = config[systemEnv]['client_id']
            # cls.instance.CLIENT_SECRET = config[systemEnv]['client_secret']
            cls.instance.CLIENT_ID = env['client_id']
            cls.instance.CLIENT_SECRET = env['client_secret']

            cls.instance.LLM_MINI_MODEL = config[systemEnv]['mini_model']
            cls.instance.LLM_FULL_MODEL = config[systemEnv]['full_model']
            cls.instance.OPENAI_MINI_MODEL = config[systemEnv]['openai_mini_model']
            cls.instance.OPENAI_MODEL = config[systemEnv]['openai_model']
            cls.instance.MAX_TOKENS = int(config[systemEnv]['max_tokens'])  
            cls.instance.UPLOAD_PATH =  config[systemEnv]["upload_path"]
            cls.instance.SENTENCE_TRANS = config[systemEnv]["defaultSentenceTransformer"]
        return cls.instance
    