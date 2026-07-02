from openai import OpenAI
from app.config.settings import settings

class EmbeddingGenerator:
    """
    Generates semantic vectors utilizing the OpenAI API.
    Provides dummy zero-vectors when API key is missing.
    """
    def __init__(self):
        self.model = settings.DEFAULT_EMBEDDINGS_MODEL
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        
        if self.api_key and self.api_key != "your_openai_api_key_here" and self.api_key.strip():
            self.client = OpenAI(api_key=self.api_key)

    def embed_documents(self, texts: list) -> list:
        if not texts:
            return []
            
        if self.client is None:
            # Fallback zero vectors
            return [[0.0] * 1536 for _ in texts]
            
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"[Warning] OpenAI embedding generation failed: {e}. Falling back to dummy vectors.")
            return [[0.0] * 1536 for _ in texts]

    def embed_query(self, text: str) -> list:
        if not text:
            return [0.0] * 1536
            
        if self.client is None:
            return [0.0] * 1536
            
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"[Warning] OpenAI query embedding failed: {e}. Returning dummy vector.")
            return [0.0] * 1536
