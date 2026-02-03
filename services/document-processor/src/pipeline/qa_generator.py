"""
Q&A Generator
Generates question-answer pairs with size-based strategies.
"""

import logging
import json
from typing import Dict, Any, List
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class QAGenerator:
    """Generate Q&A pairs using Azure OpenAI."""
    
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
    
    def generate(
        self,
        markdown: str,
        sections: List[Dict[str, str]],
        method: str,
        num_questions: int,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate Q&A pairs using appropriate method.
        
        Args:
            markdown: Full markdown document
            sections: List of sections (for per-section)
            method: "single" or "per_section"
            num_questions: Total number of Q&A pairs to generate
            metadata: Document metadata
        
        Returns:
            List of Q&A pairs: [{"question": "...", "answer": "...", "type": "..."}]
        """
        logger.info(f"Generating Q&A pairs using {method} method")
        
        if method == "single":
            return self._generate_single(markdown, num_questions, metadata)
        elif method == "per_section":
            return self._generate_per_section(sections, num_questions, metadata)
        else:
            raise ValueError(f"Unknown Q&A generation method: {method}")
    
    def _generate_single(
        self,
        markdown: str,
        num_questions: int,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate Q&A pairs with single LLM call."""
        try:
            # Truncate if needed
            max_chars = 15000
            if len(markdown) > max_chars:
                markdown = markdown[:max_chars] + "\n\n[Document truncated]"
            
            filename = metadata["original_filename"]
            doc_type = metadata["mime_type"]
            
            prompt = self._build_qa_prompt(markdown, filename, doc_type, num_questions)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at generating diverse question-answer pairs for document retrieval systems."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            qa_pairs = result.get("qa_pairs", [])
            logger.info(f"Generated {len(qa_pairs)} Q&A pairs (single-call)")
            
            return qa_pairs
            
        except Exception as e:
            logger.error(f"Single Q&A generation failed: {e}")
            return []
    
    def _generate_per_section(
        self,
        sections: List[Dict[str, str]],
        total_questions: int,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate Q&A pairs per section and merge."""
        try:
            all_qa_pairs = []
            
            # Distribute questions across sections
            questions_per_section = max(2, total_questions // len(sections))
            
            for i, section in enumerate(sections, 1):
                title = section["title"]
                content = section["content"]
                
                # Truncate very long sections
                max_chars = 5000
                if len(content) > max_chars:
                    content = content[:max_chars] + "\n[Section truncated]"
                
                logger.info(f"Generating Q&A for section {i}/{len(sections)}: {title}")
                
                prompt = f"""Generate {questions_per_section} diverse question-answer pairs for this section.

## Section: {title}

{content}

Generate questions that:
- Are self-contained (understandable without context)
- Have answers directly supported by the section
- Cover different aspects of the section
- Include various types: factual, overview, procedural, comparison, reasoning

Return JSON format:
{{
  "qa_pairs": [
    {{
      "question": "The question text",
      "answer": "The answer based on section content",
      "type": "factual|overview|procedural|comparison|reasoning"
    }}
  ]
}}

Write questions in the same language as the document."""
                
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at generating question-answer pairs from document sections."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.5,
                    max_tokens=1000,
                    response_format={"type": "json_object"}
                )
                
                result_text = response.choices[0].message.content.strip()
                result = json.loads(result_text)
                
                section_qa_pairs = result.get("qa_pairs", [])
                all_qa_pairs.extend(section_qa_pairs)
            
            # Deduplicate similar questions
            deduplicated = self._deduplicate_qa_pairs(all_qa_pairs)
            
            # Limit to requested total
            final_qa_pairs = deduplicated[:total_questions]
            
            logger.info(
                f"Generated {len(all_qa_pairs)} Q&A pairs, "
                f"deduplicated to {len(deduplicated)}, "
                f"final: {len(final_qa_pairs)}"
            )
            
            return final_qa_pairs
            
        except Exception as e:
            logger.error(f"Per-section Q&A generation failed: {e}")
            return []
    
    def _deduplicate_qa_pairs(
        self,
        qa_pairs: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Remove duplicate or very similar questions.
        Simple approach: check for exact matches and substring matches.
        """
        seen_questions = set()
        deduplicated = []
        
        for qa in qa_pairs:
            question = qa.get("question", "").lower().strip()
            
            # Skip if exact match
            if question in seen_questions:
                continue
            
            # Skip if very similar (substring of existing question)
            is_similar = False
            for seen_q in seen_questions:
                if question in seen_q or seen_q in question:
                    if abs(len(question) - len(seen_q)) < 10:
                        is_similar = True
                        break
            
            if not is_similar:
                seen_questions.add(question)
                deduplicated.append(qa)
        
        return deduplicated
    
    def _build_qa_prompt(
        self,
        content: str,
        filename: str,
        doc_type: str,
        num_questions: int
    ) -> str:
        """Build prompt for single-call Q&A generation."""
        return f"""Generate {num_questions} diverse question-answer pairs for a document retrieval system.

## Document Information
- Filename: {filename}
- Type: {doc_type}

## Document Content
{content}

## Guidelines
- Questions must be self-contained (understandable without context)
- Answers must be directly supported by the document - no assumptions
- Cover different sections and topics from the document
- Include diverse question types

## Question Types to Include
- **Factual**: Specific facts, numbers, dates, names (e.g., "What was the revenue in Q3?")
- **Overview**: General questions about purpose/topic (e.g., "What is this document about?")
- **Procedural**: How-to, processes, steps (e.g., "How do I submit a request?")
- **Comparison**: Comparing items, periods, options (e.g., "How does X compare to Y?")
- **Reasoning**: Why questions, causes, explanations (e.g., "Why did sales increase?")

## Required Output Format (JSON)
{{
  "qa_pairs": [
    {{
      "question": "The question text",
      "answer": "The answer based on document content",
      "type": "factual|overview|procedural|comparison|reasoning"
    }}
  ]
}}

Generate questions in the same language as the source document."""
