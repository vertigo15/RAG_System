import logging
import json
from typing import Dict, Any, List
from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

class Enrichment:
    """Generate summaries and Q&A pairs for sections"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, api_version: str, postgres_storage=None):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment
        self.postgres_storage = postgres_storage
        self.prompt_summary = None
        self.prompt_qa = None
    
    async def _load_prompts(self):
        """Load prompts from database settings"""
        if self.postgres_storage:
            try:
                # Get summary prompt
                summary_setting = await self.postgres_storage.get_setting('prompt_summary')
                if summary_setting:
                    self.prompt_summary = summary_setting
                
                # Get Q&A prompt
                qa_setting = await self.postgres_storage.get_setting('prompt_qa')
                if qa_setting:
                    self.prompt_qa = qa_setting
                
                logger.info("Loaded prompts from database settings")
            except Exception as e:
                logger.warning(f"Failed to load prompts from database: {e}")
    
    async def enrich_document(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summaries and Q&A pairs
        
        Args:
            tree: Output from TreeBuilder
        
        Returns:
            tree with added "enrichments" field containing summaries and Q&A
        """
        logger.info("Enriching document with summaries and Q&A")
        
        # Load prompts from database
        await self._load_prompts()
        
        sections = tree.get("structure", {}).get("sections", [])
        full_text = tree.get("text", "")
        
        # Generate document-level summary
        doc_summary = await self._generate_summary(full_text[:4000])  # First 4k chars
        
        # Generate section summaries
        section_summaries = []
        for section in sections[:5]:  # Limit to first 5 sections
            content = section.get("content", "")[:2000]  # First 2k chars per section
            if content.strip():
                summary = await self._generate_summary(content)
                section_summaries.append({
                    "section_title": section.get("title", ""),
                    "summary": summary
                })
        
        # Generate Q&A pairs
        qa_pairs = await self._generate_qa_pairs(full_text[:4000])
        
        tree["enrichments"] = {
            "document_summary": doc_summary,
            "section_summaries": section_summaries,
            "qa_pairs": qa_pairs
        }
        
        logger.info(f"Generated doc summary, {len(section_summaries)} section summaries, {len(qa_pairs)} Q&A pairs")
        return tree
    
    async def _generate_summary(self, text: str, document_title: str = "Unknown", document_type: str = "Document") -> str:
        """Generate a concise summary of text"""
        try:
            # Use custom prompt from database if available
            if self.prompt_summary:
                system_prompt = self.prompt_summary.get('system', '')
                user_template = self.prompt_summary.get('user', '')
                
                # Format user prompt with document info
                user_prompt = user_template.format(
                    document_title=document_title,
                    document_type=document_type,
                    document_content=text
                )
            else:
                # Fallback to default prompt
                system_prompt = "You are a helpful assistant that creates concise summaries. Summarize the key points in 2-3 sentences."
                user_prompt = f"Summarize the following text:\n\n{text}"
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return ""
    
    async def _generate_qa_pairs(self, text: str, document_title: str = "Unknown", document_type: str = "Document", num_pairs: int = 5) -> List[Dict[str, str]]:
        """Generate question-answer pairs from text"""
        try:
            # Use custom prompt from database if available
            if self.prompt_qa:
                system_prompt = self.prompt_qa.get('system', '')
                user_template = self.prompt_qa.get('user', '')
                
                # Format user prompt with document info
                user_prompt = user_template.format(
                    num_questions=num_pairs,
                    document_title=document_title,
                    document_type=document_type,
                    document_content=text
                )
            else:
                # Fallback to default prompt
                system_prompt = "You are a helpful assistant that generates question-answer pairs from text. Generate clear, specific questions and concise answers."
                user_prompt = f"Generate {num_pairs} question-answer pairs from the following text. Return as JSON with 'qa_pairs' array containing objects with 'question', 'answer', and 'type' fields.\n\n{text}"
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                # Remove markdown code blocks if present
                if content.startswith('```'):
                    content = content.split('```')[1]
                    if content.startswith('json'):
                        content = content[4:]
                    content = content.strip()
                
                data = json.loads(content)
                qa_pairs = data.get('qa_pairs', [])
                
                # Ensure each pair has required fields
                formatted_pairs = []
                for pair in qa_pairs:
                    if 'question' in pair and 'answer' in pair:
                        formatted_pairs.append({
                            'question': pair['question'],
                            'answer': pair['answer'],
                            'type': pair.get('type', 'general')
                        })
                
                return formatted_pairs
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse Q&A JSON response, trying fallback parsing")
                # Fallback: try to parse pipe-separated format
                qa_pairs = []
                parts = content.split("|")
                
                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts):
                        question = parts[i].replace("Q1:", "").replace("Q2:", "").replace("Q3:", "").replace("Q4:", "").replace("Q5:", "").strip()
                        answer = parts[i + 1].replace("A1:", "").replace("A2:", "").replace("A3:", "").replace("A4:", "").replace("A5:", "").strip()
                        
                        if question and answer:
                            qa_pairs.append({
                                "question": question,
                                "answer": answer,
                                "type": "general"
                            })
                
                return qa_pairs
        
        except Exception as e:
            logger.error(f"Q&A generation failed: {e}")
            return []
