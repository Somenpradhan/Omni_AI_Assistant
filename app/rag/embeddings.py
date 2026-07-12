from openai import OpenAI
from app.config.settings import settings

class EmbeddingGenerator:
    """
    Generates semantic vectors utilizing the OpenAI API.
    Falls back to a local SentenceTransformer model if OpenAI API fails or is missing.
    """
    def __init__(self):
        self.model = settings.DEFAULT_EMBEDDINGS_MODEL
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        self._local_model = None
        
        if self.api_key and self.api_key != "your_openai_api_key_here" and self.api_key.strip():
            self.client = OpenAI(api_key=self.api_key)

    def _get_local_model(self):
        if self._local_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print("[EmbeddingGenerator] Loading local sentence-transformers model (all-MiniLM-L6-v2)...")
                self._local_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"[Error] Failed to load local SentenceTransformer: {e}")
        return self._local_model

    def embed_documents(self, texts: list) -> list:
        if not texts:
            return []
            
        # Try OpenAI first
        if self.client is not None:
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.model
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                print(f"[Warning] OpenAI embedding generation failed: {e}. Falling back to local SentenceTransformer.")
        
        # Local model fallback
        local_model = self._get_local_model()
        if local_model is not None:
            try:
                embeddings = local_model.encode(texts)
                result = []
                for emb in embeddings:
                    emb_list = emb.tolist()
                    if len(emb_list) < 1536:
                        emb_list = emb_list + [0.0] * (1536 - len(emb_list))
                    result.append(emb_list)
                return result
            except Exception as e:
                print(f"[Error] Local embedding failed: {e}")
                
        # Zero fallback if all else fails
        return [[0.0] * 1536 for _ in texts]

    def embed_query(self, text: str) -> list:
        if not text:
            return [0.0] * 1536
            
        # Try OpenAI first
        if self.client is not None:
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"[Warning] OpenAI query embedding failed: {e}. Falling back to local SentenceTransformer.")
                
        # Local model fallback
        local_model = self._get_local_model()
        if local_model is not None:
            try:
                embedding = local_model.encode(text)
                emb_list = embedding.tolist()
                if len(emb_list) < 1536:
                    emb_list = emb_list + [0.0] * (1536 - len(emb_list))
                return emb_list
            except Exception as e:
                print(f"[Error] Local query embedding failed: {e}")
                
        return [0.0] * 1536
