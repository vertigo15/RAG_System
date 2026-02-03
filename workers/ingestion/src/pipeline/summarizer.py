"""
Hierarchical document summarization using Map-Reduce approach.

This module handles:
1. Splitting documents into manageable sections
2. Summarizing each section in parallel (MAP)
3. Combining section summaries into final summary (REDUCE)
4. Storing summaries with embeddings in Qdrant
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import AsyncAzureOpenAI

from src.core.logging import get_logger
from src.prompts.summary_prompts import (
    SECTION_SUMMARY_SYSTEM,
    SECTION_SUMMARY_USER,
    FINAL_SUMMARY_SYSTEM,
    FINAL_SUMMARY_USER,
    SHORT_DOC_SUMMARY_SYSTEM,
    SHORT_DOC_SUMMARY_USER
)

logger = get_logger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class SummarizerConfig:
    """Configuration for summarization."""
    
    # Size thresholds (in characters)
    short_doc_threshold: int = 12000      # ~3000 tokens - use single summary
    max_section_size: int = 15000         # ~4000 tokens - split if larger
    min_section_size: int = 500           # Skip sections smaller than this
    
    # LLM settings
    section_summary_max_tokens: int = 300
    final_summary_max_tokens: int = 800
    temperature: float = 0.3
    
    # Parallel processing
    max_concurrent_requests: int = 5


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SectionSummary:
    """Summary of a single section."""
    title: str
    summary: str
    original_length: int
    

@dataclass
class DocumentSummaries:
    """Complete summarization result."""
    document_summary: str
    section_summaries: List[SectionSummary]
    method: str  # 'single' or 'map_reduce'
    sections_count: int


# =============================================================================
# MAIN SUMMARIZER CLASS
# =============================================================================

class HierarchicalSummarizer:
    """
    Generates hierarchical summaries of documents.
    
    For short documents: Single LLM call
    For long documents: Map-Reduce approach
    
    Usage:
        summarizer = HierarchicalSummarizer(
            endpoint="https://...",
            api_key="...",
            deployment="gpt-4"
        )
        
        result = await summarizer.summarize(document_tree)
        # result.document_summary -> Final summary
        # result.section_summaries -> List of section summaries
    """
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str,
        config: Optional[SummarizerConfig] = None
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        self.api_version = api_version
        self.config = config or SummarizerConfig()
        
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        logger.info(
            "HierarchicalSummarizer initialized",
            deployment=deployment,
            short_doc_threshold=self.config.short_doc_threshold,
            max_section_size=self.config.max_section_size,
            max_concurrent_requests=self.config.max_concurrent_requests
        )
    
    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================
    
    async def summarize(self, document_tree: Dict) -> DocumentSummaries:
        """
        Generate hierarchical summary of a document.
        
        Automatically chooses between single summary (short docs)
        and map-reduce (long docs) based on document size.
        
        Args:
            document_tree: Unified document tree from tree_builder
            
        Returns:
            DocumentSummaries with document and section summaries
        """
        document_title = document_tree.get('title', 'Untitled Document')
        document_type = document_tree.get('type', 'Document')
        
        logger.info(
            "Starting hierarchical summarization",
            document_title=document_title,
            document_type=document_type
        )
        
        # Extract full text to check size
        full_text = self._extract_text_from_tree(document_tree)
        text_length = len(full_text)
        
        logger.debug(
            "Extracted document text",
            text_length=text_length,
            threshold=self.config.short_doc_threshold
        )
        
        # Choose method based on document size
        if text_length <= self.config.short_doc_threshold:
            logger.info(
                "Using single summary method (short document)",
                text_length=text_length
            )
            return await self._summarize_short_document(
                document_title=document_title,
                document_type=document_type,
                content=full_text
            )
        else:
            logger.info(
                "Using map-reduce method (long document)",
                text_length=text_length
            )
            return await self._summarize_long_document(
                document_tree=document_tree,
                document_title=document_title,
                document_type=document_type
            )
    
    # =========================================================================
    # SHORT DOCUMENT SUMMARIZATION
    # =========================================================================
    
    async def _summarize_short_document(
        self,
        document_title: str,
        document_type: str,
        content: str
    ) -> DocumentSummaries:
        """
        Summarize a short document with a single LLM call.
        """
        logger.info(
            "Starting short document summarization",
            document_title=document_title,
            content_length=len(content)
        )
        
        prompt = SHORT_DOC_SUMMARY_USER.format(
            document_title=document_title,
            document_type=document_type,
            document_content=content
        )
        
        logger.debug(
            "Generated short doc summary prompt",
            prompt_length=len(prompt)
        )
        
        summary = await self._call_llm(
            system_prompt=SHORT_DOC_SUMMARY_SYSTEM,
            user_prompt=prompt,
            max_tokens=self.config.final_summary_max_tokens,
            operation="short_document_summary"
        )
        
        logger.info(
            "Short document summarization complete",
            document_title=document_title,
            summary_length=len(summary)
        )
        
        return DocumentSummaries(
            document_summary=summary,
            section_summaries=[],
            method='single',
            sections_count=0
        )
    
    # =========================================================================
    # LONG DOCUMENT SUMMARIZATION (MAP-REDUCE)
    # =========================================================================
    
    async def _summarize_long_document(
        self,
        document_tree: Dict,
        document_title: str,
        document_type: str
    ) -> DocumentSummaries:
        """
        Summarize a long document using map-reduce.
        
        1. Split into sections
        2. MAP: Summarize each section in parallel
        3. REDUCE: Combine into final summary
        """
        logger.info(
            "Starting map-reduce summarization",
            document_title=document_title
        )
        
        # Step 1: Split document into sections
        logger.info("MAP-REDUCE: Phase 1 - Splitting document into sections")
        sections = self._split_into_sections(document_tree)
        
        logger.info(
            "Document split into sections",
            section_count=len(sections),
            avg_section_size=sum(len(s['content']) for s in sections) // len(sections) if sections else 0
        )
        
        # Step 2: MAP - Summarize each section
        logger.info(
            "MAP-REDUCE: Phase 2 - Summarizing sections in parallel",
            section_count=len(sections),
            max_concurrent=self.config.max_concurrent_requests
        )
        
        section_summaries = await self._map_summarize_sections(sections)
        
        logger.info(
            "Section summaries complete",
            summaries_count=len(section_summaries),
            total_summary_length=sum(len(s.summary) for s in section_summaries)
        )
        
        # Step 3: REDUCE - Combine into final summary
        logger.info("MAP-REDUCE: Phase 3 - Reducing to final summary")
        
        final_summary = await self._reduce_to_final_summary(
            document_title=document_title,
            document_type=document_type,
            section_summaries=section_summaries
        )
        
        logger.info(
            "Map-reduce summarization complete",
            document_title=document_title,
            final_summary_length=len(final_summary),
            section_summaries_count=len(section_summaries)
        )
        
        return DocumentSummaries(
            document_summary=final_summary,
            section_summaries=section_summaries,
            method='map_reduce',
            sections_count=len(sections)
        )
    
    # =========================================================================
    # STEP 1: SPLIT DOCUMENT INTO SECTIONS
    # =========================================================================
    
    def _split_into_sections(self, document_tree: Dict) -> List[Dict]:
        """
        Split document tree into summarizable sections.
        
        Strategy:
        1. Use existing sections from document structure
        2. If section too long, split into subsections
        3. If no clear sections, split by character count
        """
        logger.debug("Starting document splitting")
        sections = []
        
        # Try to use document's natural structure
        children = document_tree.get('children', [])
        logger.debug(
            "Processing document children",
            children_count=len(children)
        )
        
        for i, node in enumerate(children):
            if node.get('type') == 'section':
                section_text = self._extract_node_text(node)
                section_title = node.get('title', 'Untitled Section')
                
                logger.debug(
                    "Processing section",
                    section_index=i,
                    section_title=section_title,
                    section_length=len(section_text)
                )
                
                # Skip very short sections
                if len(section_text) < self.config.min_section_size:
                    logger.debug(
                        "Skipping short section",
                        section_title=section_title,
                        length=len(section_text),
                        min_size=self.config.min_section_size
                    )
                    continue
                
                # Split if too long
                if len(section_text) > self.config.max_section_size:
                    logger.debug(
                        "Section too long, splitting into subsections",
                        section_title=section_title,
                        length=len(section_text),
                        max_size=self.config.max_section_size
                    )
                    
                    subsections = self._split_long_section(
                        title=section_title,
                        content=section_text
                    )
                    sections.extend(subsections)
                    
                    logger.debug(
                        "Section split complete",
                        section_title=section_title,
                        subsection_count=len(subsections)
                    )
                else:
                    sections.append({
                        'title': section_title,
                        'content': section_text
                    })
                    logger.debug(
                        "Section added",
                        section_title=section_title,
                        length=len(section_text)
                    )
        
        # Fallback: if no sections found, split by size
        if not sections:
            logger.warning(
                "No structured sections found, using size-based splitting"
            )
            full_text = self._extract_text_from_tree(document_tree)
            sections = self._split_by_size(full_text)
            logger.info(
                "Size-based splitting complete",
                section_count=len(sections)
            )
        
        logger.info(
            "Document splitting complete",
            total_sections=len(sections),
            total_chars=sum(len(s['content']) for s in sections)
        )
        
        return sections
    
    def _split_long_section(self, title: str, content: str) -> List[Dict]:
        """Split a long section into smaller parts."""
        logger.debug(
            "Splitting long section",
            title=title,
            length=len(content)
        )
        
        parts = []
        chunk_size = self.config.max_section_size
        
        # Try to split on paragraph boundaries
        paragraphs = content.split('\n\n')
        current_chunk = ""
        part_num = 1
        
        logger.debug(
            "Section has paragraphs",
            title=title,
            paragraph_count=len(paragraphs)
        )
        
        for para_idx, para in enumerate(paragraphs):
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                parts.append({
                    'title': f"{title} (Part {part_num})",
                    'content': current_chunk.strip()
                })
                logger.debug(
                    "Created subsection",
                    title=f"{title} (Part {part_num})",
                    length=len(current_chunk),
                    paragraphs_included=para_idx
                )
                current_chunk = para
                part_num += 1
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Don't forget the last chunk
        if current_chunk.strip():
            parts.append({
                'title': f"{title} (Part {part_num})" if part_num > 1 else title,
                'content': current_chunk.strip()
            })
            logger.debug(
                "Created final subsection",
                title=f"{title} (Part {part_num})",
                length=len(current_chunk)
            )
        
        logger.info(
            "Long section split complete",
            original_title=title,
            parts_created=len(parts)
        )
        
        return parts
    
    def _split_by_size(self, text: str) -> List[Dict]:
        """Split text into chunks by size when no structure exists."""
        logger.debug(
            "Starting size-based splitting",
            text_length=len(text)
        )
        
        sections = []
        chunk_size = self.config.max_section_size
        
        # Split on paragraph boundaries
        paragraphs = text.split('\n\n')
        current_chunk = ""
        section_num = 1
        
        logger.debug(
            "Text split into paragraphs",
            paragraph_count=len(paragraphs)
        )
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                sections.append({
                    'title': f"Section {section_num}",
                    'content': current_chunk.strip()
                })
                logger.debug(
                    "Created size-based section",
                    section_num=section_num,
                    length=len(current_chunk)
                )
                current_chunk = para
                section_num += 1
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk.strip():
            sections.append({
                'title': f"Section {section_num}",
                'content': current_chunk.strip()
            })
            logger.debug(
                "Created final size-based section",
                section_num=section_num,
                length=len(current_chunk)
            )
        
        logger.info(
            "Size-based splitting complete",
            sections_created=len(sections)
        )
        
        return sections
    
    # =========================================================================
    # STEP 2: MAP - SUMMARIZE EACH SECTION
    # =========================================================================
    
    async def _map_summarize_sections(
        self,
        sections: List[Dict]
    ) -> List[SectionSummary]:
        """
        Summarize all sections in parallel.
        Uses semaphore to limit concurrent requests.
        """
        logger.info(
            "Starting parallel section summarization",
            section_count=len(sections),
            max_concurrent=self.config.max_concurrent_requests
        )
        
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def summarize_with_limit(section: Dict, index: int) -> SectionSummary:
            async with semaphore:
                logger.debug(
                    "Acquiring semaphore for section",
                    section_index=index,
                    section_title=section['title']
                )
                result = await self._summarize_single_section(section, index)
                logger.debug(
                    "Released semaphore for section",
                    section_index=index,
                    section_title=section['title']
                )
                return result
        
        tasks = [
            summarize_with_limit(section, i) 
            for i, section in enumerate(sections)
        ]
        
        logger.info(
            "Created summarization tasks",
            task_count=len(tasks)
        )
        
        summaries = await asyncio.gather(*tasks)
        
        logger.info(
            "All section summarizations complete",
            summaries_count=len(summaries)
        )
        
        return list(summaries)
    
    async def _summarize_single_section(
        self, 
        section: Dict,
        index: int
    ) -> SectionSummary:
        """Summarize a single section."""
        section_title = section['title']
        section_content = section['content'][:self.config.max_section_size]
        
        logger.info(
            "Summarizing section",
            section_index=index,
            section_title=section_title,
            content_length=len(section_content)
        )
        
        prompt = SECTION_SUMMARY_USER.format(
            section_title=section_title,
            section_content=section_content
        )
        
        logger.debug(
            "Generated section summary prompt",
            section_index=index,
            prompt_length=len(prompt)
        )
        
        summary = await self._call_llm(
            system_prompt=SECTION_SUMMARY_SYSTEM,
            user_prompt=prompt,
            max_tokens=self.config.section_summary_max_tokens,
            operation=f"section_summary_{index}"
        )
        
        result = SectionSummary(
            title=section_title,
            summary=summary,
            original_length=len(section['content'])
        )
        
        logger.info(
            "Section summary complete",
            section_index=index,
            section_title=section_title,
            summary_length=len(summary),
            compression_ratio=round(len(section['content']) / len(summary), 2)
        )
        
        return result
    
    # =========================================================================
    # STEP 3: REDUCE - COMBINE INTO FINAL SUMMARY
    # =========================================================================
    
    async def _reduce_to_final_summary(
        self,
        document_title: str,
        document_type: str,
        section_summaries: List[SectionSummary]
    ) -> str:
        """Combine all section summaries into a final document summary."""
        
        logger.info(
            "Starting reduce phase",
            document_title=document_title,
            section_summaries_count=len(section_summaries)
        )
        
        # Format section summaries for the prompt
        formatted_summaries = "\n\n".join([
            f"### {s.title}\n{s.summary}"
            for s in section_summaries
        ])
        
        logger.debug(
            "Formatted section summaries",
            formatted_length=len(formatted_summaries)
        )
        
        prompt = FINAL_SUMMARY_USER.format(
            document_title=document_title,
            document_type=document_type,
            section_summaries=formatted_summaries
        )
        
        logger.debug(
            "Generated final summary prompt",
            prompt_length=len(prompt)
        )
        
        final_summary = await self._call_llm(
            system_prompt=FINAL_SUMMARY_SYSTEM,
            user_prompt=prompt,
            max_tokens=self.config.final_summary_max_tokens,
            operation="final_summary_reduce"
        )
        
        # Calculate total compression
        original_total = sum(s.original_length for s in section_summaries)
        
        logger.info(
            "Reduce phase complete",
            document_title=document_title,
            final_summary_length=len(final_summary),
            original_total_length=original_total,
            total_compression_ratio=round(original_total / len(final_summary), 2) if final_summary else 0
        )
        
        return final_summary
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        operation: str
    ) -> str:
        """Make an LLM API call with comprehensive logging."""
        logger.debug(
            "Starting LLM call",
            operation=operation,
            system_prompt_length=len(system_prompt),
            user_prompt_length=len(user_prompt),
            max_tokens=max_tokens,
            temperature=self.config.temperature
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            
            # Log token usage if available
            if hasattr(response, 'usage') and response.usage:
                logger.info(
                    "LLM call successful",
                    operation=operation,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    response_length=len(result)
                )
            else:
                logger.info(
                    "LLM call successful",
                    operation=operation,
                    response_length=len(result)
                )
            
            return result
            
        except Exception as e:
            logger.error(
                "LLM call failed",
                operation=operation,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    def _extract_text_from_tree(self, tree: Dict) -> str:
        """Extract plain text from document tree."""
        logger.debug("Extracting text from document tree")
        lines = []
        
        def process_node(node, depth=0):
            node_type = node.get('type', 'unknown')
            
            if node_type == 'section':
                title = node.get('title', '')
                if title:
                    prefix = '#' * min(depth + 1, 4)
                    lines.append(f"\n{prefix} {title}\n")
            
            elif node_type == 'paragraph':
                content = node.get('content', '')
                if content:
                    lines.append(content)
            
            elif node_type == 'table':
                headers = node.get('headers', [])
                rows = node.get('rows', [])
                if headers:
                    lines.append('\n| ' + ' | '.join(str(h) for h in headers) + ' |')
                    lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                for row in rows:
                    lines.append('| ' + ' | '.join(str(cell) for cell in row) + ' |')
                lines.append('')
            
            elif node_type == 'image':
                description = node.get('description', '')
                if description:
                    lines.append(f"\n[Image: {description}]\n")
            
            for child in node.get('children', []):
                process_node(child, depth + 1)
        
        process_node(tree)
        result = '\n'.join(lines)
        
        logger.debug(
            "Text extraction complete",
            extracted_length=len(result),
            line_count=len(lines)
        )
        
        return result
    
    def _extract_node_text(self, node: Dict) -> str:
        """Extract text from a single node and its children."""
        lines = []
        
        def process(n):
            if n.get('type') == 'paragraph':
                lines.append(n.get('content', ''))
            elif n.get('type') == 'table':
                headers = n.get('headers', [])
                rows = n.get('rows', [])
                if headers:
                    lines.append(' | '.join(str(h) for h in headers))
                for row in rows:
                    lines.append(' | '.join(str(cell) for cell in row))
            elif n.get('type') == 'image':
                lines.append(f"[Image: {n.get('description', '')}]")
            
            for child in n.get('children', []):
                process(child)
        
        process(node)
        return '\n'.join(lines)
