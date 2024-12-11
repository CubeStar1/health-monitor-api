import cohere
from typing import List
import os

co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

def generate_embedding(text: str) -> List[float]:
    response = co.embed(texts=[text], model="embed-english-v3.0", input_type="search_document", embedding_types=['float'])
    return response.embeddings.float[0]