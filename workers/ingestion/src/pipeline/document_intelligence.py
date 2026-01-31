import logging
from typing import Dict, Any, List
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

logger = logging.getLogger(__name__)

class DocumentIntelligenceProcessor:
    """Extract text and structure using Azure Document Intelligence"""
    
    def __init__(self, endpoint: str, key: str):
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """
        Extract document content using prebuilt-layout model
        
        Returns:
            {
                "text": str,  # Full text
                "pages": List[Dict],  # Page-level info
                "tables": List[Dict],  # Extracted tables
                "paragraphs": List[Dict],  # Paragraph structure
                "styles": List[Dict]  # Font styles
            }
        """
        logger.info(f"Processing document with Document Intelligence: {file_path}")
        
        try:
            with open(file_path, "rb") as f:
                poller = self.client.begin_analyze_document(
                    "prebuilt-layout",
                    document=f
                )
            
            result = poller.result()
            
            # Extract all text
            full_text = result.content
            
            # Extract pages
            pages = []
            for page in result.pages:
                pages.append({
                    "page_number": page.page_number,
                    "width": page.width,
                    "height": page.height,
                    "unit": page.unit,
                    "lines": [{"text": line.content, "polygon": line.polygon} for line in page.lines] if page.lines else []
                })
            
            # Extract tables
            tables = []
            if result.tables:
                for table in result.tables:
                    table_data = {
                        "row_count": table.row_count,
                        "column_count": table.column_count,
                        "cells": []
                    }
                    for cell in table.cells:
                        table_data["cells"].append({
                            "row_index": cell.row_index,
                            "column_index": cell.column_index,
                            "content": cell.content,
                            "row_span": cell.row_span,
                            "column_span": cell.column_span
                        })
                    tables.append(table_data)
            
            # Extract paragraphs
            paragraphs = []
            if result.paragraphs:
                for para in result.paragraphs:
                    paragraphs.append({
                        "content": para.content,
                        "role": para.role if hasattr(para, 'role') else None,
                        "bounding_regions": [
                            {
                                "page_number": region.page_number,
                                "polygon": region.polygon
                            }
                            for region in para.bounding_regions
                        ] if para.bounding_regions else []
                    })
            
            # Extract styles
            styles = []
            if result.styles:
                for style in result.styles:
                    styles.append({
                        "is_handwritten": style.is_handwritten,
                        "confidence": style.confidence
                    })
            
            logger.info(f"Extracted {len(pages)} pages, {len(tables)} tables, {len(paragraphs)} paragraphs")
            
            return {
                "text": full_text,
                "pages": pages,
                "tables": tables,
                "paragraphs": paragraphs,
                "styles": styles
            }
            
        except Exception as e:
            logger.error(f"Document Intelligence processing failed: {e}")
            raise
