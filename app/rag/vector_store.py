import os
import json
import math
from app.rag.embeddings import EmbeddingGenerator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_FILE = os.getenv("VECTOR_DB_PATH", os.path.join(BASE_DIR, "vector_db", "db.json"))

class LocalVectorStore:
    """
    A pure-Python FAISS-mimicking vector database that persists documents and their
    embeddings to a JSON file. Cosine similarity is computed via dot products.
    Falls back to text keyword matching if embeddings are unpopulated (all zero vectors).
    """
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.embeddings_generator = EmbeddingGenerator()
        self.load()

    def load(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.embeddings = data.get("embeddings", [])
            except Exception as e:
                print(f"[Warning] Failed loading local vector db: {e}")

    def save(self):
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "documents": self.documents,
                    "embeddings": self.embeddings
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Failed saving local vector db: {e}")

    def add_chunks(self, chunks: list):
        """
        Input format: list of dicts with keys "page_content" and "metadata"
        """
        if not chunks:
            return
            
        texts = [c["page_content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        
        # Generate vectors
        vectors = self.embeddings_generator.embed_documents(texts)
        
        for text, meta, vector in zip(texts, metadatas, vectors):
            self.documents.append({
                "page_content": text,
                "metadata": meta
            })
            self.embeddings.append(vector)
            
        self.save()

    def delete_document_chunks(self, doc_title: str):
        """
        Deletes all chunks belonging to a specific document title.
        """
        indices_to_keep = []
        for idx, doc in enumerate(self.documents):
            # Check if source metadata matches
            source = doc.get("metadata", {}).get("source", "")
            if source != doc_title and doc_title not in source:
                indices_to_keep.append(idx)
                
        self.documents = [self.documents[i] for i in indices_to_keep]
        self.embeddings = [self.embeddings[i] for i in indices_to_keep]
        self.save()
        print(f"[VectorStore] Cleaned chunks for doc: {doc_title}")

    def similarity_search(self, query: str, k: int = 5) -> list:
        if not self.documents:
            return []
            
        query_vector = self.embeddings_generator.embed_query(query)
        is_query_simulated = all(v == 0.0 for v in query_vector)
        
        scores = []
        for idx, doc_vector in enumerate(self.embeddings):
            is_doc_simulated = all(v == 0.0 for v in doc_vector)
            
            if not is_query_simulated and not is_doc_simulated:
                # Cosine similarity
                dot_product = sum(q * d for q, d in zip(query_vector, doc_vector))
                q_len = math.sqrt(sum(q * q for q in query_vector))
                d_len = math.sqrt(sum(d * d for d in doc_vector))
                
                if q_len > 0 and d_len > 0:
                    score = dot_product / (q_len * d_len)
                else:
                    score = 0.0
            else:
                # Keyword similarity fallback
                score = self._keyword_score(query, self.documents[idx]["page_content"])
                
            scores.append((score, idx))
            
        # Sort by score desc
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, idx in scores[:k]:
            results.append({
                "page_content": self.documents[idx]["page_content"],
                "metadata": self.documents[idx]["metadata"],
                "score": score
            })
        return results

    def _keyword_score(self, query: str, text: str) -> float:
        qw = set(query.lower().replace("?", "").replace(".", "").split())
        tw = text.lower().split()
        if not qw or not tw:
            return 0.0
        matches = sum(1 for w in qw if w in tw)
        return matches / (len(qw) + 1.0)

vector_store = LocalVectorStore()
