from app.rag.vector_store import vector_store
from app.rag.document_loader import DocumentLoader
from app.rag.chunker import DocumentChunker
import os

class RAGService:
    @staticmethod
    def process_and_ingest_file(file_path: str) -> dict:
        """
        Loads document chunks, embeds them, and saves to local vector database.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # 1. Load document content
        if ext == ".pdf":
            documents = DocumentLoader.load_pdf(file_path)
        elif ext == ".txt":
            documents = DocumentLoader.load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        if not documents:
            return {"status": "empty", "chunks_added": 0}
            
        # 2. Chunk documents
        chunker = DocumentChunker()
        all_chunks = []
        for doc in documents:
            chunks = chunker.split_text(doc["page_content"], doc["metadata"])
            all_chunks.extend(chunks)
            
        # 3. Add to vector store
        vector_store.add_chunks(all_chunks)
        
        return {
            "status": "success",
            "filename": filename,
            "chunks_added": len(all_chunks)
        }

    @staticmethod
    def delete_document(doc_title: str) -> bool:
        """
        Deletes a document's chunks from vector database.
        """
        try:
            vector_store.delete_document_chunks(doc_title)
            return True
        except Exception as e:
            print(f"[ERROR] Failed deleting document chunks: {e}")
            return False
            
    @staticmethod
    def list_documents() -> list:
        """
        Lists all document titles currently tracked inside the vector store metadata.
        """
        titles = set()
        for doc in vector_store.documents:
            source = doc.get("metadata", {}).get("source", "")
            if source:
                titles.add(source)
        return list(titles)
