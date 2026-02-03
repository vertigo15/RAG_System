"""
LLM service for text generation tasks using Azure OpenAI.
"""

import logging
import pandas as pd
from openai import AzureOpenAI
from openai import RateLimitError, APIError

logger = logging.getLogger(__name__)


class LLMService:
    """GPT-4o service for text generation tasks."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str,
        deployment_name: str,
        timeout: int = 30
    ):
        """
        Initialize LLM service.
        
        Args:
            endpoint: Azure OpenAI endpoint
            api_key: API key
            api_version: API version
            deployment_name: Chat deployment name
            timeout: Request timeout in seconds
        """
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            timeout=timeout
        )
        self.deployment_name = deployment_name
    
    def summarize_table(
        self,
        df: pd.DataFrame,
        sheet_name: str = "",
        sample_rows: int = 20
    ) -> str:
        """
        Generate a summary of table data.
        
        Args:
            df: Pandas DataFrame
            sheet_name: Name of the sheet (for Excel files)
            sample_rows: Number of sample rows to include
            
        Returns:
            Summary text
        """
        try:
            # Get basic info
            row_count = len(df)
            columns = list(df.columns)
            
            # Create sample table
            sample_df = df.head(sample_rows)
            sample_table = sample_df.to_markdown(index=False)
            
            # Build prompt
            prompt = self._build_table_prompt(
                sheet_name=sheet_name,
                columns=columns,
                row_count=row_count,
                sample_table=sample_table
            )
            
            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a data analyst summarizing spreadsheet data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            logger.debug(f"Generated table summary: {summary[:100]}...")
            return summary
            
        except RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            return "[Table summary unavailable - rate limit]"
        except APIError as e:
            logger.error(f"API error: {e}")
            return "[Table summary unavailable - API error]"
        except Exception as e:
            logger.error(f"Failed to summarize table: {e}")
            return "[Table summary unavailable]"
    
    def _build_table_prompt(
        self,
        sheet_name: str,
        columns: list,
        row_count: int,
        sample_table: str
    ) -> str:
        """
        Build prompt for table summarization.
        
        Args:
            sheet_name: Sheet name
            columns: List of column names
            row_count: Total row count
            sample_table: Markdown table of sample data
            
        Returns:
            Prompt text
        """
        sheet_info = f"Sheet name: {sheet_name}\n" if sheet_name else ""
        
        return f"""Summarize this spreadsheet data in 3-5 sentences.

{sheet_info}Columns: {', '.join(columns)}
Total rows: {row_count}

Sample data (first {min(20, row_count)} rows):
{sample_table}

Describe:
1. What data this table contains
2. What the columns represent
3. Any notable patterns visible in the sample
4. The scale of the data (how many rows, date ranges if applicable)

Be concise and factual."""
