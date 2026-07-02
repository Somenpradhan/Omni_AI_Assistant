import os
import pypdf

class DocumentLoader:
    @staticmethod
    def load_pdf(file_path: str) -> list:
        """
        Extracts content from a PDF file using pypdf.
        Returns a list of dicts: {"page_content": text, "metadata": {"source": filename, "page": page_number}}
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")
            
        filename = os.path.basename(file_path)
        documents = []
        
        try:
            reader = pypdf.PdfReader(file_path)
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    documents.append({
                        "page_content": text,
                        "metadata": {
                            "source": filename,
                            "page": i,
                            "path": file_path
                        }
                    })
            return documents
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {file_path}: {e}")
            raise e

    @staticmethod
    def load_txt(file_path: str) -> list:
        """
        Reads a standard text document.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Text file not found at {file_path}")
            
        filename = os.path.basename(file_path)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return [{
                "page_content": content,
                "metadata": {
                    "source": filename,
                    "path": file_path
                }
            }]
        except Exception as e:
            print(f"[ERROR] Failed to load text file {file_path}: {e}")
            raise e
