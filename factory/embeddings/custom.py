from sentence_transformers import SentenceTransformer
from typing import List

class CustomEmbeddings:
    def __init__(self, modelName=None):
        modelName = modelName or "sentence-transformers/all-MiniLM-L6-v2" #default model
        #"sentence-transformers/all-roberta-large-v1"
        self.model = SentenceTransformer(modelName)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.model.encode(t).tolist() for t in texts]
    
    def embed_query(self, query: str) -> List[float]:
        return self.model.encode([query])[0].tolist()