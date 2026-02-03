"""
Summarizer
Generates document summaries with size-based strategies.
"""

import logging
from typing import Dict, Any, List
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class Summarizer:
    """Generate document summaries using Azure OpenAI."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str,
        deployment_name: str
    ):
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = deployment_name
    
    def summarize(
        self,
        markdown: str,
        sections: List[Dict[str, str]],
        method: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Generate document summary using appropriate method.
        
        Args:
            markdown: Full markdown document
            sections: List of sections (for map-reduce)
            method: "single" or "map_reduce"
            metadata: Document metadata
        
        Returns:
            Summary text
        """
        logger.info(f"Generating summary using {method} method")
        
        if method == "single":
            return self._summarize_single(markdown, metadata)
        elif method == "map_reduce":
            return self._summarize_map_reduce(sections, metadata)
        else:
            raise ValueError(f"Unknown summarization method: {method}")
    
    def _summarize_single(
        self,
        markdown: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Generate summary with single LLM call."""
        try:
            # For medium docs, truncate if needed
            max_chars = 15000
            if len(markdown) > max_chars:
                markdown = markdown[:max_chars] + "\n\n[Document truncated for summarization]"
            
            filename = metadata["original_filename"]
            doc_type = metadata["mime_type"]
            
            prompt = self._build_summary_prompt(markdown, filename, doc_type)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert document analyst. Create clear, accurate, and comprehensive summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated single-call summary ({len(summary)} chars)")
            
            return summary
            
        except Exception as e:
            logger.error(f"Single summarization failed: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _summarize_map_reduce(
        self,
        sections: List[Dict[str, str]],
        metadata: Dict[str, Any]
    ) -> str:
        """Generate summary using map-reduce approach."""
        try:
            # Step 1: Summarize each section (MAP)
            section_summaries = []
            
            for i, section in enumerate(sections, 1):
                title = section["title"]
                content = section["content"]
                
                # Truncate very long sections
                max_chars = 5000
                if len(content) > max_chars:
                    content = content[:max_chars] + "\n[Section truncated]"
                
                logger.info(f"Summarizing section {i}/{len(sections)}: {title}")
                
                prompt = f"""Summarize this section of the document:

## Section: {title}

{content}

Provide a concise summary (2-3 sentences) focusing on key points."""
                
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at summarizing document sections concisely."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=200
                )
                
                section_summary = response.choices[0].message.content.strip()
                section_summaries.append(f"**{title}**: {section_summary}")
            
            # Step 2: Combine section summaries (REDUCE)
            logger.info("Combining section summaries")
            
            combined_summaries = "\n\n".join(section_summaries)
            filename = metadata["original_filename"]
            
            reduce_prompt = f"""Create a comprehensive summary of the document based on these section summaries:

Document: {filename}

{combined_summaries}

Provide a unified summary with:
1. Overview (2-3 sentences)
2. Key Points (3-5 bullet points)
3. Main Conclusions (if applicable)

Write in the same language as the document."""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating comprehensive document summaries."
                    },
                    {
                        "role": "user",
                        "content": reduce_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            final_summary = response.choices[0].message.content.strip()
            logger.info(f"Generated map-reduce summary ({len(final_summary)} chars)")
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Map-reduce summarization failed: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _build_summary_prompt(
        self,
        content: str,
        filename: str,
        doc_type: str
    ) -> str:
        """Build prompt for single-call summarization."""
        return f"""Create a clear, accurate, and comprehensive summary of this document.

## Document Information
- Filename: {filename}
- Type: {doc_type}

## Document Content
{content}

## Required Output Structure

### Overview
A 2-3 sentence high-level description of what this document is about.

### Key Points
The most important information (3-7 bullet points).

### Important Data
- Key numbers, statistics, percentages
- Important dates or deadlines
- Names of people, organizations, or products
- Specific requirements or conditions

### Conclusions
Main conclusions, recommendations, or action items (if present in the document).

Target length: 200-400 words. Write in the same language as the source document."""
