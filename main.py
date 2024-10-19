from fastapi import FastAPI, Body,File, Form, UploadFile, Response, status, Request,APIRouter, HTTPException, Cookie
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from typing import Annotated
import os,shutil,uuid
from datetime import datetime, timedelta 
from secret import VaultSecret
from config import GlobalConfig
from util.pylogger import LogUtility
from controllers.summarize import Summarizer
from controllers.chat import ChatFlow
from factory.llm.huggingface import HfInferenceApiClient
from objectServices.documentService import DocQueryService

from unique_names_generator import get_random_name
from unique_names_generator.data import ADJECTIVES, STAR_WARS

logger=LogUtility.get_logger("AISummarizer")
vault = VaultSecret()
token = vault.getOauth2Token()
vault.GetSecrets(token)
config = GlobalConfig()

class ChatItemModel(BaseModel):
    documentid: str
    prompt: str 
    chattopicid: str

app = FastAPI()
app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")
templates = Jinja2Templates(directory="view")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(
    prefix="/api/v1/docs",
    tags=["docs"]
)
@router.get("/")
async def get_all_docs():
    docQuerySvc = DocQueryService(config, logger)
    return docQuerySvc.GetAllDocs()

@router.post("/upload/")
async def create_file(
    file: Annotated[UploadFile, File()],
    #documentId: Annotated[str, Form()],
    response: Response
):
    documentId = str(uuid.uuid4())
    try:
        uploadfile1 = save_uploaded_file(file.filename)

        with open(uploadfile1, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        summarizer = Summarizer()
        summarizer.Summarize(documentId,file.filename, uploadfile1)
        return {"status":"ok"}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status":"error", "message":e}
    
app.include_router(router)

chatRouter = APIRouter(
    prefix="/api/v1/chat",
    tags=["chat"]
)
@chatRouter.post("/topic/new")
async def newTopic(request: Request, response: Response, sentence:Annotated[str, Form()]):
    anonuserid = get_anon_userid(request, response)
    chatFlow = ChatFlow()
    result = chatFlow.SetChatTopic(anonuserid, sentence)
    return result

@chatRouter.get("/topic")
async def getAllTopic(request: Request, response: Response):
    anonuserid = get_anon_userid(request, response)
    chatFlow = ChatFlow()
    result = chatFlow.GetAllChatTopics(anonuserid)
    return result

@chatRouter.get("/topic/user/{username}}")
async def getAllTopic(username):
    chatFlow = ChatFlow()
    result = chatFlow.GetAllChatTopics(username)
    return result

@chatRouter.get("/topic/{id}")
async def getTopic(request: Request, response: Response, id):
    anonuserid = get_anon_userid(request, response)
    chatFlow = ChatFlow()
    result = chatFlow.GetChatTopicHistory(anonuserid, id)
    return result

@chatRouter.post("/")
async def chat_flow(request: Request, response: Response, chatItem: Annotated[ChatItemModel, Form()]):
    anonuserid = get_anon_userid(request, response)
    chatFlow = ChatFlow()
    result = chatFlow.Chat(anonuserid, chatItem.chattopicid, chatItem.prompt, chatItem.documentid )
    return result

app.include_router(chatRouter)

@app.get("/")
async def main(request: Request):
    try:     
        anonuserid = request.cookies.get('anonuserid')
        if anonuserid==None:       
           anonuserid = get_random_name(separator="-", style="lowercase")
        return templates.TemplateResponse('chat.html', {'request': request, 'anonuserid': anonuserid})
    except Exception as e:
        print (e)

# @app.post("/newTopic")
# def cookie(request: Request, response: Response, sentence:Annotated[str, Form()]):
#     anonuserid = get_anon_userid(request, response)
#     chatFlow = ChatFlow()
#     result = chatFlow.SetChatTopic(anonuserid, sentence)
#     return result

# @app.post("/test")
# async def test(instruction, text):
#     hfApi = HfInferenceApiClient(config.LLM_MINI_MODEL, config.HF_KEY)
#     result = hfApi.Query(instruction, text, 10000)
#     return result




# @app.post("/upload/")
# async def create_file(
#     file: Annotated[UploadFile, File()],
#     #documentId: Annotated[str, Form()],
#     response: Response
# ):
#     documentId = str(uuid.uuid4())
#     try:
#         uploadfile1 = save_uploaded_file(file.filename)

#         with open(uploadfile1, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
        
#         summarizer = Summarizer()
#         summarizer.Summarize(documentId,file.filename, uploadfile1)
#         return {"status":"ok"}
#     except Exception as e:
#         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#         return {"status":"error", "message":e}

@staticmethod
def save_uploaded_file(uploadedFileName: str):
    _, file_extension = os.path.splitext(uploadedFileName)
    filename = uuid.uuid4().hex + file_extension      
    uploadfile = os.path.join(config.UPLOAD_PATH, filename)
    return uploadfile

def get_anon_userid(request:Request, response: Response):
    anonuserid = request.cookies.get('anonuserid')
    print(anonuserid)
    if anonuserid==None:
        anonuserid = get_random_name(separator="-", style="lowercase")
        expires = datetime.utcnow() + timedelta(days=365)
        response.set_cookie(key="anonuserid", value=anonuserid,expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),httponly=True,samesite='lax')
        print(request.cookies.get('anonuserid'))
    return anonuserid

# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app)