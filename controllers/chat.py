from util.pylogger import LogUtility
from factory.chunk.tokenUtil import GetNumOfTokens 
from factory.llm.huggingface import HfInferenceApiClient
from factory.llm.openai import OpenAIClient
from objectServices.chatHistoryService import ChatHistoryService, ChatTopicService
from config import GlobalConfig
from factory.llm.model.instruct import InstructionList
import sys, json
from objectServices.documentService import DocQueryService

class ChatFlow:
    def __init__(self):
        self.logger = LogUtility.get_logger(__name__)
        self.globalConfig = GlobalConfig()
        self.hfKey = self.globalConfig.HF_KEY
        self.maxTokens = 4096
        self.embeddingsModel = self.globalConfig.SENTENCE_TRANS
        self.llmMiniModel = self.globalConfig.LLM_MINI_MODEL
        self.llmModel = self.globalConfig.LLM_FULL_MODEL #"meta-llama/Llama-3.1-8B-Instruct"
        #=========================================================
        #Run debug log
        #===========================================================
        self.logger.info("Query initiated sucessfully!")
        self.logger.info(self.__dict__)

    def Chat(self, anonuserid, chatTopicId, userPromptText, documentId=None):
        funcName = sys._getframe().f_code.co_name
        self.documentId = documentId
        context = ''
        chatResponse = ''
        self.logger.info(f'{funcName}: start: {anonuserid}: {chatTopicId} : {documentId} : {userPromptText}')   
        try:
            #======================================================
            #todo: Get chat history in DB
            #todo: Tokenize it before passing to llm
            #=======================================================            
            chatHistoryService = ChatHistoryService(self.globalConfig, self.logger)
            results = chatHistoryService.Get(anonuserid, chatTopicId)
            for res in results:
                context += f'user: {res[0]}\nsystem: {res[1]}\n'

            if documentId!='0':
                # Analyze prompt
                response = self.analyzePromptText(documentId, userPromptText)
                
                #clean json string
                jsonRes = self._cleanJsonRes(response)

                # Semantic Search vector DB
                sourceText = self.searchVectorDB(documentId, jsonRes)                
            
                # Send to LLM to generate response            
                chatResponse = self.chatWithDoc(anonuserid, userPromptText, jsonRes["user_primary_goal"], context, sourceText)
                         
            else:
                chatResponse = self.generalChat(anonuserid, userPromptText, context)

            chatHistoryService.Set(anonuserid, chatTopicId, userPromptText, chatResponse)

            self.logger.debug("============================================================")
            self.logger.debug(chatResponse)
            self.logger.info(f'{funcName}: end: {documentId}')   

            return chatResponse
        except Exception as e:
            self.logger.error(f'{funcName}: {e}')
            self.logger.error(f'{funcName}: anonuserid: {anonuserid}')
            self.logger.error(f'{funcName}: Document ID: {documentId}')
            self.logger.error(f'{funcName}: Question: {userPromptText}')
            self.logger.error(f'{funcName}: context: {context}')    
            raise

    def analyzePromptText(self,documentId, userPromptText):
        funcName = sys._getframe().f_code.co_name
        self.documentId = documentId     

        try:
            # Analyze prompt
            self.logger.info(f'{funcName}: start: {documentId} : Analyze Prompt: {userPromptText}')
            hfInferApiClient = HfInferenceApiClient(self.llmModel, self.hfKey, self.logger)
            promptText = InstructionList["promptAnalyzer"].replace("[prompttext]", userPromptText)            
            response = hfInferApiClient.Query(promptText, self.maxTokens)             
            self.logger.info(f'{funcName}: {response}')            
           
            return response
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: Request Id: [{self.documentId}] : {e}')     
            self.logger.error(f'{sys._getframe().f_code.co_name}: Request Id: [{self.documentId}] : Prompt: {userPromptText}')        
            raise

    def searchVectorDB(self, documentId, jsonRes):        
        funcName = sys._getframe().f_code.co_name
        self.logger.info(f'{funcName}: start: {documentId} : Semantic Search vector DB')
        try:
            docQuerySvc = DocQueryService(self.globalConfig, self.logger)
            
            sourceText =""
            for item in jsonRes["outline_of_response"]:
                self.logger.debug(item)
                docQueryRes = docQuerySvc.Query(documentId, item, 3)
                #self.logger.debug(docQueryRes)               
                for res in docQueryRes:
                    sourceText += res[0]

            self.logger.debug(f'{sys._getframe().f_code.co_name}: {GetNumOfTokens(sourceText)}')
            return sourceText
        except Exception as e:
            jsonStr =json.dumps(jsonRes)
            self.logger.error(f'{sys._getframe().f_code.co_name}: Document Id: [{self.documentId}] : {e}') 
            self.logger.error(f'{sys._getframe().f_code.co_name}: Document Id: [{self.documentId}] : {jsonStr}') 
            raise

    def chatWithDoc(self, anonuserid, question, userGoal, context, sourceMaterial)->str:
        funcName = sys._getframe().f_code.co_name
        self.logger.info(f'{funcName}: start: {anonuserid} : {question}')
        try:
            userPrompt = f"The previous chat history with user is {context}. Current question is : {question} with goal of {userGoal}. \n***content: {sourceMaterial}"
            openai = OpenAIClient(self.globalConfig.OPENAI_KEY, self.globalConfig.OPENAI_MINI_MODEL, self.logger)
            return openai.Chat(InstructionList["summarySystemInstruction"], userPrompt)
        except Exception as e:            
            self.logger.error(f'{funcName}: {e}')
            self.logger.error(f'{funcName}: anonuserid: {anonuserid}')
            self.logger.error(f'{funcName}: Document ID: {self.documentId}')
            self.logger.error(f'{funcName}: Question: {question}')
            self.logger.error(f'{funcName}: userGoal: {userGoal}')
            self.logger.error(f'{funcName}: context: {context}')
            self.logger.error(f'{funcName}: sourceMaterial: {sourceMaterial}')
            raise

    def generalChat(self, anonuserid, question, context = None)->str:
        funcName = sys._getframe().f_code.co_name
        self.logger.info(f'{funcName}: start: {anonuserid} : {question}')
       
        try:            
            userPrompt = f"You are a helpful assistant. The previous chat history with user is {context}. Now the user is having question of : {question}. "
            openai = OpenAIClient(self.globalConfig.OPENAI_KEY, self.globalConfig.OPENAI_MODEL, self.logger)
            response = openai.GeneralChat(userPrompt)
            
            return response
        except Exception as e:            
            self.logger.error(f'{funcName}: {e}')
            self.logger.error(f'{funcName}: Document ID: {anonuserid}')
            self.logger.error(f'{funcName}: Question: {question}')
            self.logger.error(f'{funcName}: context: {context}')
            raise

    def _cleanJsonRes(self, jsonStr)->json:
        funcName = sys._getframe().f_code.co_name
        self.logger.debug(f'{funcName}: start:')
        try:
            jsonStr = jsonStr.strip()
            if jsonStr.startswith("```json") or jsonStr.startswith("```"):
                jsonStr = jsonStr.removeprefix("```json").removeprefix("```").removesuffix("```")
            return json.loads(jsonStr)
        except Exception as e:
            self.logger.error(f'{funcName}: {e}')
            self.logger.error(f'{funcName}: {jsonStr}')

    
    def CreateChatTopic(self, sentence):
        promptText = f"Summarize the following sentence in less than 6 words: {sentence}"
        hfInferApiClient = HfInferenceApiClient(self.llmMiniModel, self.hfKey, self.logger)
        response = hfInferApiClient.Query(promptText, self.maxTokens)  
        return response   
    
    def SetChatTopic(self, anonuserid, sentence):
        topic = self.CreateChatTopic(sentence)
        chatTopicSvc = ChatTopicService(self.globalConfig, self.logger)
        chatTopicId = chatTopicSvc.Set(anonuserid, topic)
        return {"id":chatTopicId, "topic":topic}   
    
    def GetAllChatTopics(self, anonuserid):
        allChatTopics = []
        chatTopicSvc = ChatTopicService(self.globalConfig, self.logger)
        result = chatTopicSvc.GetAll(anonuserid)
        for res in result:
            #print(res)
            allChatTopics.append({"id":res[0], "topic":res[3]})
        return allChatTopics 
    
    def GetChatTopicHistory(self, anonuserid, topicId):
        # chatHistoryResult = {}
        # chatTopic = {}
        # chatTopicSvc = ChatTopicService(self.globalConfig, self.logger)
        # result = chatTopicSvc.Get(anonuserid, topicId)
        # for res in result:
        #     chatTopic = {"id":res[0], "topic":res[2]}

        chatHistory = []
        chatHistoryService = ChatHistoryService(self.globalConfig, self.logger)
        results = chatHistoryService.Get(anonuserid, topicId)
        for res in results:
            #print(res)
            chatHistory.append({'user': res[0], "system": res[1]})
        return chatHistory
        # chatHistoryResult["chatTopic"] = chatTopic
        # chatHistoryResult["chatHistory"] = chatHistory
        # return chatHistoryResult 
