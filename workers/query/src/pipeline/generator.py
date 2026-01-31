import logging
from typing import List, Dict, Any
from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

class Generator:
    """Generate final answer with citations"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, api_version: str):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment
    
    async def generate_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate answer with citations
        
        Returns:
            {
                "answer": str,
                "citations": List[Dict]
            }
        """
        logger.info(f"Generating answer for query: {query[:100]}...")
        
        if not chunks:
            return {
                "answer": "I don't have enough information to answer this question.",
                "citations": []
            }
        
        try:
            # Build context with citations
            context_parts = []
            for i, chunk in enumerate(chunks):
                context_parts.append(f"[{i+1}] {chunk.get('text', '')}")
            
            context = "\n\n".join(context_parts)
            
            prompt = f"""Answer the question based on the provided context. Include citation numbers [1], [2], etc. when referencing specific information.

Question: {query}

Context:
{context}

Answer (with citations):"""
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context. Always cite your sources using [1], [2], etc."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Extract citations
            citations = []
            for i, chunk in enumerate(chunks):
                citation_num = i + 1
                if f"[{citation_num}]" in answer:
                    citations.append({
                        "citation_number": citation_num,
                        "text": chunk.get("text", ""),
                        "section": chunk.get("section", ""),
                        "document_id": chunk.get("document_id", ""),
                        "type": chunk.get("type", "")
                    })
            
            logger.info(f"Generated answer with {len(citations)} citations")
            
            return {
                "answer": answer,
                "citations": citations
            }
        
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "citations": []
            }
