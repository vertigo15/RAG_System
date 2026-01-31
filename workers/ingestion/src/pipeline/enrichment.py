import logging
from typing import Dict, Any, List
from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

class Enrichment:
    """Generate summaries and Q&A pairs for sections"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, api_version: str):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment
    
    async def enrich_document(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summaries and Q&A pairs
        
        Args:
            tree: Output from TreeBuilder
        
        Returns:
            tree with added "enrichments" field containing summaries and Q&A
        """
        logger.info("Enriching document with summaries and Q&A")
        
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
    
    async def _generate_summary(self, text: str) -> str:
        """Generate a concise summary of text"""
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise summaries. Summarize the key points in 2-3 sentences."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize the following text:\n\n{text}"
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return ""
    
    async def _generate_qa_pairs(self, text: str, num_pairs: int = 3) -> List[Dict[str, str]]:
        """Generate question-answer pairs from text"""
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates question-answer pairs from text. Generate clear, specific questions and concise answers."
                    },
                    {
                        "role": "user",
                        "content": f"Generate {num_pairs} question-answer pairs from the following text. Format as Q1:|A1:|Q2:|A2:|Q3:|A3:\n\n{text}"
                    }
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse Q&A pairs
            qa_pairs = []
            parts = content.split("|")
            
            for i in range(0, len(parts) - 1, 2):
                if i + 1 < len(parts):
                    question = parts[i].replace("Q1:", "").replace("Q2:", "").replace("Q3:", "").strip()
                    answer = parts[i + 1].replace("A1:", "").replace("A2:", "").replace("A3:", "").strip()
                    
                    if question and answer:
                        qa_pairs.append({
                            "question": question,
                            "answer": answer
                        })
            
            return qa_pairs
        
        except Exception as e:
            logger.error(f"Q&A generation failed: {e}")
            return []
