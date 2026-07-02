from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.upload import UploadResponse
from app.services.upload_service import UploadService
from app.services.rag_service import RAGService
from typing import List

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a domain PDF or TXT document, segments chunks, and creates vector store embeddings.
    """
    if not file.filename.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT documents are supported.")
        
    try:
        result = await UploadService.save_and_ingest(file)
        return UploadResponse(
            filename=result["filename"],
            status=result["status"],
            chunks_added=result["chunks_added"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload and ingestion failed: {str(e)}")

@router.get("/documents", response_model=List[str])
def list_documents():
    """
    Lists unique source document filenames currently stored in the vector store.
    """
    try:
        return RAGService.list_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/document/{title}")
def delete_document(title: str):
    """
    Deletes all chunks and vector indices associated with the document title.
    """
    try:
        success = RAGService.delete_document(title)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or delete failed.")
        return {"status": "deleted", "title": title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
