from app.llm.provider import get_chat_completion
from app.llm.output_parser import parse_json
import json

class Reranker:
    @staticmethod
    def rerank(query: str, chunks: list, top_n: int = 3) -> list:
        """
        Reranks matching chunks based on semantic relevance to query using LLM score evaluation.
        Falls back to original vector scores if LLM is unavailable or unpopulated.
        """
        if not chunks:
            return []
            
        # If we have only a few chunks, we can return them directly or check relevance
        if len(chunks) <= top_n:
            return chunks
            
        # We will use the LLM to score the relevance of each chunk from 0 to 10
        scored_chunks = []
        
        # Prepare batch content to score to minimize token calls
        prompt_items = []
        for i, chunk in enumerate(chunks):
            prompt_items.append(f"--- CHUNK {i} ---\n{chunk['page_content']}")
            
        prompt = f"""You are an advanced RAG reranking agent. Evaluate how relevant each of the following text chunks is to the user's query.
User Query: "{query}"

For each chunk, assign a relevance score between 0 (not relevant at all) and 10 (extremely relevant, contains direct answers).

{chr(10).join(prompt_items)}

Respond with a JSON object containing a list of scores for each chunk:
{{
  "scores": [
    {{"index": 0, "score": 8.5}},
    {{"index": 1, "score": 2.0}}
  ]
}}
"""
        try:
            # Low temperature for deterministic scoring
            response = get_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                json_mode=True
            )
            data = parse_json(response)
            scores_list = data.get("scores", [])
            
            # Map scores to chunks
            scores_map = {item["index"]: item["score"] for item in scores_list if "index" in item and "score" in item}
            
            for i, chunk in enumerate(chunks):
                # Fallback to store vector search score if LLM score is absent
                llm_score = scores_map.get(i, chunk.get("score", 0.0) * 10)
                chunk_copy = chunk.copy()
                chunk_copy["rerank_score"] = llm_score
                scored_chunks.append(chunk_copy)
                
            # Sort by rerank score descending
            scored_chunks.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
            return scored_chunks[:top_n]
            
        except Exception as e:
            print(f"[Warning] Reranker LLM call failed: {e}. Falling back to cosine similarity scores.")
            # Fallback sorting by original score
            chunks_copy = [c.copy() for c in chunks]
            chunks_copy.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            return chunks_copy[:top_n]
