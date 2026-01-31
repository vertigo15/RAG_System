import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Chunker:
    """Semantic chunking with configurable size and overlap"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create semantic chunks from document tree
        
        Args:
            tree: Enriched document tree
        
        Returns:
            List of chunks with metadata
        """
        logger.info(f"Chunking document with size={self.chunk_size}, overlap={self.chunk_overlap}")
        
        chunks = []
        full_text = tree.get("text", "")
        sections = tree.get("structure", {}).get("sections", [])
        enrichments = tree.get("enrichments", {})
        
        # Chunk main text
        text_chunks = self._create_text_chunks(full_text)
        
        for idx, chunk_text in enumerate(text_chunks):
            # Find which section this chunk belongs to
            section_title = self._find_section(chunk_text, sections)
            
            chunks.append({
                "chunk_id": f"chunk_{idx}",
                "text": chunk_text,
                "type": "text_chunk",
                "section": section_title,
                "position": idx,
                "metadata": {
                    "chunk_size": len(chunk_text.split()),
                    "total_chunks": len(text_chunks)
                }
            })
        
        # Add summaries as chunks
        doc_summary = enrichments.get("document_summary", "")
        if doc_summary:
            chunks.append({
                "chunk_id": "summary_doc",
                "text": doc_summary,
                "type": "summary",
                "section": "Document Summary",
                "position": -1,
                "metadata": {"level": "document"}
            })
        
        for idx, section_summary in enumerate(enrichments.get("section_summaries", [])):
            chunks.append({
                "chunk_id": f"summary_section_{idx}",
                "text": section_summary.get("summary", ""),
                "type": "summary",
                "section": section_summary.get("section_title", ""),
                "position": -1,
                "metadata": {"level": "section"}
            })
        
        # Add Q&A pairs as chunks
        for idx, qa in enumerate(enrichments.get("qa_pairs", [])):
            qa_text = f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}"
            chunks.append({
                "chunk_id": f"qa_{idx}",
                "text": qa_text,
                "type": "qa",
                "section": "Q&A",
                "position": -1,
                "metadata": {
                    "question": qa.get("question", ""),
                    "answer": qa.get("answer", "")
                }
            })
        
        logger.info(f"Created {len(chunks)} chunks ({len(text_chunks)} text, {len(enrichments.get('section_summaries', [])) + 1} summaries, {len(enrichments.get('qa_pairs', []))} Q&A)")
        return chunks
    
    def _create_text_chunks(self, text: str) -> List[str]:
        """Create overlapping text chunks by tokens (words)"""
        words = text.split()
        chunks = []
        
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            
            # Move start forward, accounting for overlap
            start += self.chunk_size - self.chunk_overlap
            
            # Break if we've reached the end
            if end >= len(words):
                break
        
        return chunks
    
    def _find_section(self, chunk_text: str, sections: List[Dict]) -> str:
        """Find which section a chunk belongs to (simple heuristic)"""
        # Simple approach: find if chunk contains section title
        for section in sections:
            title = section.get("title", "")
            if title and title.lower() in chunk_text.lower():
                return title
        
        return "Main Content"
