import re
from typing import List

class CitationService:
    @staticmethod
    def extract_sources(context: str) -> List[str]:
        """
        Parses context strings for source metadata tags.
        Example matched format: '--- Excerpt from filename.pdf ---'
        """
        if not context:
            return []
            
        pattern = r"--- Excerpt from ([^\n\-]+) ---"
        found = re.findall(pattern, context)
        
        unique_sources = []
        for item in found:
            clean_item = item.strip()
            if clean_item and clean_item not in unique_sources:
                unique_sources.append(clean_item)
                
        return unique_sources

    @staticmethod
    def format_citations_markdown(sources: List[str]) -> str:
        """
        Compiles a list of source paths/names into a clean, readable markdown footer block.
        """
        if not sources:
            return ""
            
        header = "\n\n**Sources & Documents Ingested:**"
        items = [f"- `{s}`" for s in sources]
        return f"{header}\n" + "\n".join(items)
