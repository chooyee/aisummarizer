import sys
from typing import List
from factory.vectordb.pgClientBase import PgClientBaseClass

class PgClient(PgClientBaseClass):
    def __init__(self, config):
        super().__init__(config)

    def __enter__(self):
        try:         
            return self
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise

    def ExecuteTxn(self, sqlQuery, paramList):
        numOftxn = 0
        try:
            
            cur = self.conn.cursor()
            with self.conn.transaction():
                for param in paramList:
                    cur.execute(sqlQuery, param) 
                    numOftxn +=1
            
            return numOftxn
        except Exception as e:            
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            self.logger.debug(sqlQuery)
            self.logger.debug(paramList)
            raise

    def Execute(self, sqlQuery, params):        
        try:
            return self.conn.execute(sqlQuery, params)
        except Exception as e:            
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            self.logger.debug(sqlQuery)
            self.logger.debug(params)
            raise

    def ExecuteGetLastID(self, sqlQuery, params):        
        try:
            cur = self.conn.cursor()
            cur.execute(sqlQuery, params)
            new_id = cur.fetchone()[0]
            return new_id
        except Exception as e:            
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            self.logger.debug(sqlQuery)
            self.logger.debug(params)
            raise

    def Query(self, sqlQuery, param=None)->List:
        try:           
            #sqlQuery = f'SELECT * FROM tblrag ORDER BY tblrag.summarized_vector <-> %s LIMIT 5'
            response = self.conn.execute(sqlQuery, param).fetchall()
            return response
        except Exception as e:            
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            self.logger.debug(sqlQuery)
            self.logger.debug(param)
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        if not self.conn.closed:
             self.conn.close()

