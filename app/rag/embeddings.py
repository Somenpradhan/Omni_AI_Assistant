from app.config.settings import settings

class EmbeddingGenerator:
    """
    Generates semantic vectors utilizing a local SentenceTransformer model.
    Pads vectors to 1536 dimensions for compatibility.
    """
    def __init__(self):
        self._local_model = None

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
                
        return [[0.0] * 1536 for _ in texts]

    def embed_query(self, text: str) -> list:
        if not text:
            return [0.0] * 1536
            
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

