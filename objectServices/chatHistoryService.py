from factory.vectordb.pgClient import PgClient
import sys

class ChatHistoryService:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def Get(self, anonuserid, chatTopicId):
        sqlQuery = f"select userprompt,gptanswer from tblchathistory where chattopicid =%s and anonuserid= %s"
        try:
            with PgClient(self.config) as pgc:
                respone = pgc.Query(sqlQuery, (chatTopicId, anonuserid))
                return respone
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            raise            

    def Set(self, anonuserid, chatTopicId, userPrompt, gptAnswer):
        sqlQuery = f"insert into tblchathistory (anonuserid, chattopicid, userprompt, gptanswer) values (%s,%s,%s,%s)"
        try:
            with PgClient(self.config) as pgc:
                respone = pgc.Execute(sqlQuery, (anonuserid, chatTopicId, userPrompt, gptAnswer))
                return respone
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            raise            

class ChatTopicService:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def GetAll(self, anonuserid):
        sqlQuery = f"select * from tblchattopic where anonuserid= %s order by created_at desc"
        try:
            with PgClient(self.config) as pgc:
                respone = pgc.Query(sqlQuery, (anonuserid,))
                return respone
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            raise       

    # def Get(self, anonuserid, topicId):
    #     sqlQuery = f"select * from tblchattopic where anonuserid= %s and id= %s"
    #     try:
    #         with PgClient(self.config) as pgc:
    #             respone = pgc.Query(sqlQuery, (anonuserid,topicId))
    #             return respone
    #     except Exception as e:
    #         self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
    #         raise           
    
    def Get(self, anonuserid, topicId):
        sqlQuery = f"select * from tblchattopic where anonuserid= %s and id= %s"
        try:
            with PgClient(self.config) as pgc:
                respone = pgc.Query(sqlQuery, (anonuserid,topicId))
                return respone
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            raise           

    def Set(self, anonuserid, topic):
        funcName = sys._getframe().f_code.co_name
        sqlQuery = f"insert into tblchattopic (anonuserid, topic) values (%s,%s) RETURNING id;"
        try:
            with PgClient(self.config) as pgc:
                respone = pgc.ExecuteGetLastID(sqlQuery, (anonuserid, topic))
                self.logger.debug(f'{funcName}: Chat Topic Id: {respone}')
                return respone
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            raise            
  