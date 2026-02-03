"""
Vision service for image description using Azure OpenAI GPT-4o.
"""

import logging
import base64
import asyncio
from typing import List, Dict, Optional
from openai import AzureOpenAI
from openai import RateLimitError, APIError

logger = logging.getLogger(__name__)


class VisionService:
    """GPT-4o vision service for image descriptions."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str,
        deployment_name: str,
        timeout: int = 30
    ):
        """
        Initialize vision service.
        
        Args:
            endpoint: Azure OpenAI endpoint
            api_key: API key
            api_version: API version
            deployment_name: Vision deployment name
            timeout: Request timeout in seconds
        """
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            timeout=timeout
        )
        self.deployment_name = deployment_name
    
    def describe_image(self, image_bytes: bytes, context: str = "") -> str:
        """
        Generate description for an image.
        
        Args:
            image_bytes: Image binary data
            context: Optional context from surrounding document
            
        Returns:
            Image description text
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Build prompt
            prompt = self._build_prompt(context)
            
            # Call GPT-4o vision
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            description = response.choices[0].message.content.strip()
            logger.debug(f"Generated image description: {description[:100]}...")
            return description
            
        except RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            return "[Image: description unavailable - rate limit]"
        except APIError as e:
            logger.error(f"API error: {e}")
            return "[Image: description unavailable - API error]"
        except Exception as e:
            logger.error(f"Failed to describe image: {e}")
            return "[Image: description unavailable]"
    
    async def describe_images_batch(
        self,
        images: List[Dict[str, any]],
        max_concurrent: int = 5
    ) -> List[Dict[str, str]]:
        """
        Describe multiple images with controlled concurrency.
        
        Args:
            images: List of dicts with 'bytes' and optional 'context'
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of dicts with 'image_id' and 'description'
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def describe_with_semaphore(image_data: Dict) -> Dict:
            async with semaphore:
                # Run sync method in executor
                loop = asyncio.get_event_loop()
                description = await loop.run_in_executor(
                    None,
                    self.describe_image,
                    image_data['bytes'],
                    image_data.get('context', '')
                )
                return {
                    'image_id': image_data['image_id'],
                    'description': description
                }
        
        tasks = [describe_with_semaphore(img) for img in images]
        results = await asyncio.gather(*tasks)
        
        logger.info(f"Described {len(results)} images")
        return results
    
    def _build_prompt(self, context: str) -> str:
        """
        Build prompt for image description.
        
        Args:
            context: Context from surrounding document
            
        Returns:
            Prompt text
        """
        base_prompt = """Describe this image for a document search index.

Include:
1. What type of image this is (chart, diagram, photo, screenshot, etc.)
2. For charts: the chart type, axis labels, data trends, key values
3. For diagrams: the components and their relationships
4. For photos: the subject and notable details
5. Any text visible in the image
6. Specific numbers, dates, or names that appear

Be factual and specific. Write 2-5 sentences."""

        if context:
            return f"{base_prompt}\n\nContext from the surrounding document: {context}"
        
        return base_prompt
