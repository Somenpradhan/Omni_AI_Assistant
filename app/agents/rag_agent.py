from app.rag.retriever import Retriever
from app.rag.reranker import Reranker

def rag_agent(query: str, top_k: int = 5, top_n: int = 3) -> dict:
    """
    Fetches domains documents and applies Reranker scores to return top context.
    """
    # 1. Retrieve initial candidate chunks
    retrieved = Retriever.retrieve(query, k=top_k)
    
    if not retrieved:
        return {
            "context": "No document chunks retrieved.",
            "documents_retrieved": [],
            "sources": []
        }
        
    # 2. Rerank candidates using cross-encoder LLM checking
    reranked = Reranker.rerank(query, retrieved, top_n=top_n)
    
    # 3. Compile context text and metadata summaries
    context_chunks = []
    doc_titles = set()
    sources = set()
    
    for item in reranked:
        context_chunks.append(item["page_content"])
        meta = item.get("metadata", {})
        source_name = meta.get("source", "Unknown PDF")
        doc_titles.add(source_name)
        if "page" in meta:
            sources.add(f"{source_name} (Page {meta['page']})")
        else:
            sources.add(source_name)
            
    final_context = "\n\n".join(
        f"--- Excerpt from {item.get('metadata', {}).get('source', 'Document')} ---\n{item['page_content']}"
        for item in reranked
    )
    
    return {
        "context": final_context,
        "documents_retrieved": list(doc_titles),
        "sources": list(sources)
    }
