from factory.chunk.semanticChunking import SemanticTextChunker
from factory.supabase.supaclient import Supaclient
from typing import Literal, List
from enum import Enum
from util.pylogger import LogUtility
from factory.chunk.tokenUtil import GetNumOfTokens 
from factory.chunk.models.chunkData import ChunkDataModel
from factory.llm.huggingface import HfInferenceApiClient
from config import GlobalConfig
from factory.embeddings.custom import CustomEmbeddings
from factory.llm.model.instruct import InstructionList
import sys, os

class FileType(Enum):
    PDF = "pdf"
    TEXT = "txt"


class Summarizer:
    def __init__(self):

        self.logger = LogUtility.get_logger(__name__)
        self.textChunker = SemanticTextChunker()
        self.globalConfig = GlobalConfig()
        self.summarizerModel = self.globalConfig.LLM_MINI_MODEL
        self.hfKey = self.globalConfig.HF_KEY
        self.maxTokens = self.globalConfig.MAX_TOKENS
        self.embeddingsModel = self.globalConfig.SENTENCE_TRANS

        #=========================================================
        #Run debug log
        #===========================================================
        self.logger.debug("Summarizer initiated sucessfully!")
        self.logger.debug(self.__dict__)

    def Summarize(self, documentId, fileName, filePath):
        self.logger.info(f"Summarize request [{documentId}]: started with file:{filePath}")
        self.documentId = documentId
        try:     

            fileType = ""
            _, extension = os.path.splitext(fileName)
            match extension:
                case '.pdf':
                    fileType = FileType.PDF
                case '.txt':
                    fileType = FileType.TEXT
                case '_':
                    raise Exception(f"Unsupported file type: {extension}!")
            
            self.logger.info(f"TextChunking request [{documentId}]: Start")
            chunkList = self._textChunking(documentId, filePath, fileType)
            self.logger.info(f"LLM query request [{documentId}]: Start")
            chunkList = self._query(chunkList)
                       
            self.logger.info(f"Save to DB request [{documentId}]: Start")
            with Supaclient(self.globalConfig, self.logger) as supabase:
                response = (
                    supabase.table("tbldoc")
                    .insert({"doc_name":fileName, "doc_path":filePath, "document_id":documentId})
                    .execute()
                )
                #print(response)
                response = (
                    supabase.table("tblrag")
                    .insert(chunkList)
                    .execute()
                )
            
            self.logger.info(f"Summarize request [{documentId}]: End")
            return response
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: Request Id: [{self.documentId}] : {e}')
            raise

    def _textChunking(self, documentId, filePath, fileType: Literal[FileType.PDF, FileType.TEXT])->List:
        #self.logger.debug("_textChunking: Start")
        chunkList = []
        try:
            if fileType==FileType.PDF:
                semantic_chunks = self.textChunker.SplitPDF(filePath)
            else:
                semantic_chunks = self.textChunker.SplitText(filePath)
            
            for i, semantic_chunk in enumerate(semantic_chunks):
                # print(semantic_chunk.page_content)
                token = GetNumOfTokens(semantic_chunk.page_content)
                if token < 1:
                    continue

                if token < 200 and len(chunkList)>0:
                    chunkData = ChunkDataModel(**chunkList[-1])
                    chunkData.chunk +=  semantic_chunk.page_content
                    chunkData.chunk_token = int(chunkData.chunk_token) + int(token)
                    chunkList[-1] = chunkData.model_dump()
                else:
                    chunkData = ChunkDataModel(document_id=documentId, chunk_id=i+1, chunk=semantic_chunk.page_content, chunk_token=token)
                    chunkList.append(chunkData.model_dump())
                    #chunkList.append({"request_id": documentId, "chunk_id":i+1, "chunk":semantic_chunk.page_content, "chunk_token":token})
                    #chunkList.append(ChunkData(i+1, semantic_chunk.page_content, token))
                # if i>1:
                #     break
            #self.logger.debug("_textChunking: End")
            return chunkList
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: Request Id: [{self.documentId}] : {e}')
            raise
        
    def _query(self, chunkList):
        #self.logger.debug("_query: Start")
        instruction = InstructionList["disect"]
        try:
            embeddings = CustomEmbeddings(self.embeddingsModel)
            hfInferApiClient = HfInferenceApiClient(self.summarizerModel, self.hfKey, self.logger)
            for chunkData in chunkList:
                content = chunkData["chunk"]
                userPrompt = f"{instruction} \n***content\n{content}"
                response = hfInferApiClient.Query(userPrompt, self.maxTokens)
                chunkData["summarized_chunk"] = response
                chunkData["summarized_vector"] = embeddings.embed_query(response)
            return chunkList
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: Request Id: [{self.documentId}] : {e}')
            raise