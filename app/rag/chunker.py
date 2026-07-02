class DocumentChunker:
    """
    Modular text splitter that divides documents into manageable chunks.
    Bypasses PyTorch langchain-text-splitters.
    """
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str, metadata: dict = None) -> list:
        if not text:
            return []
            
        metadata = metadata or {}
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Find natural word/line boundaries
            if end < len(text):
                boundary = -1
                sub_str = text[start:end]
                for sep in ["\n\n", "\n", ". ", " "]:
                    idx = sub_str.rfind(sep)
                    # Only cut if boundary is deep enough
                    if idx > int(self.chunk_size * 0.7):
                        boundary = start + idx + len(sep)
                        break
                if boundary != -1:
                    end = boundary

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "page_content": chunk_text,
                    "metadata": metadata.copy()
                })
            
            if end >= len(text):
                break
            # Step overlap backwards
            start = max(start + 1, end - self.chunk_overlap)
            
        return chunks
