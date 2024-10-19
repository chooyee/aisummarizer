from factory.vectordb.vectorDBClient import VectorDBClient
from factory.vectordb.pgClient import PgClient
from sentence_transformers import SentenceTransformer
import numpy as np, sys

class DocQueryService:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def GetAllDocs(self):
        sqlQuery = f"select document_id, doc_name from tbldoc"
        try:
            with PgClient(self.config) as pgc:
                respone = pgc.Query(sqlQuery)
                return respone
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            raise            

    def Query(self, documentId, searchText, limit:int = 5):
        sqlQuery = f"select summarized_chunk from tblrag where document_id = %s ORDER BY tblrag.summarized_vector <-> %s LIMIT {limit}"
        try:
            with VectorDBClient(self.config) as vdc:
                respone = vdc.Query(sqlQuery, (documentId, self.GetEmbedding(searchText)))
                return respone
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            self.logger.debug(f'documentId: {documentId}')
            self.logger.debug(f'searchText: {searchText}')
            raise            

    def GetEmbedding(self, text):
        embeddingModelName = self.config.SENTENCE_TRANS
        embeddingModel = SentenceTransformer(embeddingModelName) 
        return np.array(embeddingModel.encode([text])[0].tolist())