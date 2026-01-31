import logging
import json
from typing import Dict, Any, List
from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

class Agent:
    """Agentic evaluation of retrieval quality"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, api_version: str):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment
    
    async def evaluate(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        iteration: int,
        max_iterations: int
    ) -> Dict[str, Any]:
        """
        Evaluate whether retrieved chunks are sufficient to answer query
        
        Returns:
            {
                "decision": "proceed" | "refine_query" | "expand_search",
                "confidence": float,
                "reasoning": str,
                "refined_query": str | null
            }
        """
        logger.info(f"Agent evaluating iteration {iteration}/{max_iterations}")
        
        # If last iteration, always proceed
        if iteration >= max_iterations:
            return {
                "decision": "proceed",
                "confidence": 1.0,
                "reasoning": "Maximum iterations reached, proceeding with available information",
                "refined_query": None
            }
        
        try:
            # Create context from chunks
            context = "\n\n".join([
                f"{chunk.get('text', '')[:300]}..."
                for chunk in chunks[:5]
            ])
            
            prompt = f"""You are an AI agent evaluating whether retrieved information is sufficient to answer a query.

Query: {query}

Retrieved Information:
{context}

Evaluate the quality and sufficiency of the retrieved information. Choose ONE action:
1. "proceed" - Information is sufficient to answer the query
2. "refine_query" - Information is insufficient, suggest a refined query
3. "expand_search" - Information is partially relevant, expand search scope

Respond in JSON format:
{{
  "decision": "proceed|refine_query|expand_search",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "refined_query": "new query if refine_query, else null"
}}"""
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an evaluation agent. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON
            try:
                # Try to extract JSON if wrapped in markdown
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(result_text)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse agent response: {result_text}")
                # Default to proceed
                result = {
                    "decision": "proceed",
                    "confidence": 0.8,
                    "reasoning": "Agent evaluation inconclusive, proceeding with available information",
                    "refined_query": None
                }
            
            logger.info(f"Agent decision: {result.get('decision')} (confidence: {result.get('confidence', 0)})")
            return result
        
        except Exception as e:
            logger.error(f"Agent evaluation failed: {e}")
            # Default to proceed
            return {
                "decision": "proceed",
                "confidence": 0.5,
                "reasoning": f"Agent evaluation error: {str(e)}",
                "refined_query": None
            }
