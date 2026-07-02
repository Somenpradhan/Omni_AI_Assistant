from app.rag.vector_store import vector_store

class Retriever:
    @staticmethod
    def retrieve(query: str, k: int = 6) -> list:
        """
        Retrieves matching chunks from vector store.
        """
        try:
            return vector_store.similarity_search(query, k=k)
        except Exception as e:
            print(f"[ERROR] Retriever failed: {e}")
            return []
