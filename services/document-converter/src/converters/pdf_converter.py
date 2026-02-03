"""
PDF converter using Azure Document Intelligence.
"""

import logging
import time
import uuid
from io import BytesIO
from typing import List, Dict, Any
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from converters.base import BaseConverter
from models import ConversionResult, ImageInfo, TableInfo
from utils.markdown_helpers import create_markdown_table, format_header, sanitize_for_markdown

logger = logging.getLogger(__name__)


class PDFConverter(BaseConverter):
    """Convert PDF files to markdown using Azure Document Intelligence."""
    
    def __init__(
        self,
        doc_intelligence_endpoint: str,
        doc_intelligence_key: str,
        vision_service=None,
        llm_service=None,
        enable_image_descriptions: bool = True
    ):
        """
        Initialize PDF converter.
        
        Args:
            doc_intelligence_endpoint: Azure Document Intelligence endpoint
            doc_intelligence_key: API key
            vision_service: VisionService for image descriptions
            llm_service: LLMService (not used for PDF)
            enable_image_descriptions: Whether to generate image descriptions
        """
        super().__init__(vision_service, llm_service)
        self.doc_client = DocumentAnalysisClient(
            endpoint=doc_intelligence_endpoint,
            credential=AzureKeyCredential(doc_intelligence_key)
        )
        self.enable_image_descriptions = enable_image_descriptions
    
    def get_file_type(self) -> str:
        return "pdf"
    
    def convert(self, file_bytes: bytes, filename: str, document_id: str = None) -> tuple:
        """
        Convert PDF to markdown.
        
        Args:
            file_bytes: PDF binary data
            filename: Original filename
            document_id: Document UUID (optional, for result)
            
        Returns:
            Tuple of (markdown_content, ConversionResult)
        """
        start_time = time.time()
        document_id = document_id or str(uuid.uuid4())
        
        try:
            logger.info(f"Converting PDF: {filename}")
            
            # Step 1: Analyze document with Document Intelligence
            poller = self.doc_client.begin_analyze_document(
                "prebuilt-layout",
                document=BytesIO(file_bytes)
            )
            result = poller.result()
            
            logger.info(f"Document Intelligence extraction complete: {len(result.pages)} pages")
            
            # Step 2: Extract and process components
            images_info = []
            tables_info = []
            
            # Process tables
            if result.tables:
                for idx, table in enumerate(result.tables):
                    table_id = f"table_{idx+1}"
                    tables_info.append(TableInfo(
                        table_id=table_id,
                        row_count=table.row_count,
                        column_count=table.column_count,
                        has_summary=False
                    ))
            
            # Step 3: Convert to markdown
            markdown = self._build_markdown(result, images_info, tables_info)
            
            # Step 4: Create result
            processing_time = time.time() - start_time
            conversion_result = self._create_success_result(
                document_id=document_id,
                filename=filename,
                markdown=markdown,
                processing_time=processing_time,
                images=images_info,
                tables=tables_info
            )
            
            logger.info(f"PDF conversion complete: {len(markdown)} chars, {processing_time:.2f}s")
            return markdown, conversion_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"PDF conversion failed: {e}", exc_info=True)
            
            error_result = self._create_error_result(
                document_id=document_id,
                filename=filename,
                error=str(e),
                processing_time=processing_time
            )
            return None, error_result
    
    def _build_markdown(
        self,
        result: Any,
        images_info: List[ImageInfo],
        tables_info: List[TableInfo]
    ) -> str:
        """
        Build markdown from Document Intelligence result.
        
        Args:
            result: Document Intelligence result
            images_info: List to populate with image info
            tables_info: List to populate with table info
            
        Returns:
            Markdown string
        """
        markdown_parts = []
        
        # Add page count
        if result.pages:
            markdown_parts.append(f"*Document with {len(result.pages)} pages*\n\n---\n")
        
        # Process paragraphs
        if result.paragraphs:
            for para in result.paragraphs:
                content = para.content.strip()
                if not content:
                    continue
                
                role = getattr(para, 'role', None)
                
                if role == "title":
                    markdown_parts.append(format_header(content, 1))
                elif role == "sectionHeading":
                    markdown_parts.append(format_header(content, 2))
                elif role in ["pageHeader", "pageFooter"]:
                    markdown_parts.append(f"*{content}*")
                elif role == "pageNumber":
                    continue  # Skip page numbers
                else:
                    markdown_parts.append(content)
        elif result.content:
            # Fallback to full text if no paragraphs
            markdown_parts.append(sanitize_for_markdown(result.content))
        
        # Add tables
        if result.tables:
            markdown_parts.append("\n\n## Tables\n")
            for idx, table in enumerate(result.tables):
                markdown_parts.append(f"\n### Table {idx + 1}\n")
                table_md = self._convert_table(table)
                if table_md:
                    markdown_parts.append(table_md)
        
        return "\n\n".join(markdown_parts)
    
    def _convert_table(self, table: Any) -> str:
        """
        Convert Document Intelligence table to markdown.
        
        Args:
            table: Table object from Document Intelligence
            
        Returns:
            Markdown table string
        """
        row_count = table.row_count
        col_count = table.column_count
        cells = table.cells
        
        if not cells or row_count == 0 or col_count == 0:
            return ""
        
        # Build 2D grid
        grid = [["" for _ in range(col_count)] for _ in range(row_count)]
        
        for cell in cells:
            row_idx = cell.row_index
            col_idx = cell.column_index
            content = cell.content.replace("\n", " ").strip()
            
            if row_idx < row_count and col_idx < col_count:
                grid[row_idx][col_idx] = content
        
        # Convert to markdown
        if row_count > 0:
            headers = grid[0]
            rows = grid[1:] if row_count > 1 else []
            return create_markdown_table(headers, rows)
        
        return ""
