import unittest
from app.rag.vector_store import vector_store

class TestRAGRetriever(unittest.TestCase):
    def test_keyword_matching_fallback(self):
        # Direct verification of the keyword similarity score fallback engine
        score = vector_store._keyword_score("What does the manual say about Aether Orchestrator?", "This is a document about Aether Orchestrator system manual.")
        self.assertGreater(score, 0.0)

    def test_similarity_search_returns_list(self):
        # Checks that vector search returns structured result list
        results = vector_store.similarity_search("Aether Orchestrator manual", k=2)
        self.assertIsInstance(results, list)
        if len(results) > 0:
            self.assertIn("page_content", results[0])
            self.assertIn("metadata", results[0])

if __name__ == "__main__":
    unittest.main()
