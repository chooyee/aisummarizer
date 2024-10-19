from pydantic import BaseModel
from typing import List, Optional

# Define the Pydantic model
class ChunkDataModel(BaseModel):
    document_id: str
    chunk_id: int
    chunk: str
    chunk_token: int
    summarized_chunk: Optional[str] = None
    summarized_vector: Optional[List[float]] = None

if __name__ == "__main__":
    data = {
        "document_id": "12345",
        "chunk_id": 1,
        "chunk": "This is a sample chunk.",
        "chunk_token": 100,
        "summarized_chunk": "abcde12345",
        "summarized_vector":"[0.111]"
    }

    # Convert dictionary to Pydantic model
    request_model = ChunkDataModel(document_id="12345",
        chunk_id=1,
        chunk="This is a sample chunk.",
        chunk_token=100,
        summarized_chunk="summary",
        summarized_vector=[0.1,0.3]
        )
    
    print(request_model.model_dump())
