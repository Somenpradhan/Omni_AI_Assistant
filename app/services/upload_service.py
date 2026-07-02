import os
from fastapi import UploadFile
from app.config.settings import settings
from app.services.rag_service import RAGService
from app.database import crud
from app.database.database import SessionLocal

class UploadService:
    @staticmethod
    async def save_and_ingest(file: UploadFile) -> dict:
        """
        Saves uploaded file stream locally and schedules database text embedding ingestion.
        """
        db = SessionLocal()
        filename = file.filename
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Save file to disk
        try:
            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)
        except Exception as e:
            db.close()
            raise IOError(f"Failed to write file to disk: {e}")
            
        # Log upload transaction
        db_file = None
        try:
            db_file = crud.models.UploadedFile(filename=filename, filepath=filepath, status="pending")
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
        except Exception as e:
            print(f"[Warning] Failed to log upload entry: {e}")
            
        # Run chunking & vector store ingestion
        try:
            result = RAGService.process_and_ingest_file(filepath)
            
            # Update status in db
            if db_file:
                db_file.status = "processed"
                
            # Log document entry
            doc_entry = crud.models.Document(
                title=filename,
                source_path=filepath,
                file_size=len(content)
            )
            db.add(doc_entry)
            db.commit()
            
            return {
                "filename": filename,
                "status": "success",
                "chunks_added": result.get("chunks_added", 0)
            }
        except Exception as e:
            if db_file:
                db_file.status = "failed"
                db.commit()
            raise e
        finally:
            db.close()
