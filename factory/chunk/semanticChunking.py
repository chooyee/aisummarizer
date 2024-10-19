from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
import sys
from util.pylogger import LogUtility
from factory.embeddings.custom import CustomEmbeddings

# class MyEmbeddings:
#     def __init__(self):
#         self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

#     def embed_documents(self, texts: List[str]) -> List[List[float]]:
#         return [self.model.encode(t).tolist() for t in texts]

class SemanticTextChunker:
    def __init__(self, modelName = None):        
        modelName = modelName or "sentence-transformers/all-MiniLM-L6-v2" #default model
        print("model="+modelName)
        embeddings = CustomEmbeddings(modelName)
        # Using HuggingFace embeddings with SemanticChunker
        self.text_splitter = SemanticChunker(embeddings)
        self.logger = LogUtility.get_logger(__name__)

    def SplitPDF(self, pdf):
        try:
            loader = PyPDFLoader(pdf)
            documents = loader.load()
            semantic_chunks = self.text_splitter.split_documents(documents)
            return semantic_chunks
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise

    def SplitText(self, textFile):
        try:
            with open(textFile, "r", encoding='utf-8') as file:
                text = file.read()
        
            semantic_chunks = self.text_splitter.create_documents([text])
            return semantic_chunks
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise


if __name__ == "__main__":
    semanticTextChunker = SemanticTextChunker()
    # semantic_chunks = semanticTextChunker.SplitPDF('./docs/svb-review-20230428.pdf')
    semantic_chunks = semanticTextChunker.SplitText('./docs/state_of_the_union.txt')
    for i, semantic_chunk in enumerate(semantic_chunks):
        print(f"Chunk {i+1}:")
        print(semantic_chunk.page_content)
        #print(f"Total Tokens: {GetNumOfTokens(semantic_chunk.page_content)}")


