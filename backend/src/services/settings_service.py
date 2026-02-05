"""
Settings service for configuration management.
"""

from typing import Dict, Any
from src.repositories.settings_repository import SettingsRepository
from src.models.schemas import SettingsUpdate, SettingsResponse
from src.core.logging import get_logger

logger = get_logger(__name__)


class SettingsService:
    """Service for settings operations."""
    
    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo
    
    async def get_settings(self) -> SettingsResponse:
        """Get all settings."""
        all_settings = await self.settings_repo.get_all()
        
        return SettingsResponse(
            azure_openai_endpoint=all_settings.get("azure_openai_endpoint", ""),
            azure_openai_api_key=all_settings.get("azure_openai_api_key", ""),
            azure_embedding_deployment=all_settings.get("azure_embedding_deployment", "text-embedding-3-large"),
            azure_llm_deployment=all_settings.get("azure_llm_deployment", "gpt-4"),
            azure_doc_intelligence_endpoint=all_settings.get("azure_doc_intelligence_endpoint", ""),
            azure_doc_intelligence_key=all_settings.get("azure_doc_intelligence_key", ""),
            default_top_k=all_settings.get("default_top_k", 10),
            default_rerank_top=all_settings.get("default_rerank_top", 5),
            max_agent_iterations=all_settings.get("max_agent_iterations", 3),
            chunk_size=all_settings.get("chunk_size", 512),
            chunk_overlap=all_settings.get("chunk_overlap", 50),
            # Chunking Configuration (new fields)
            semantic_overlap_enabled=all_settings.get("semantic_overlap_enabled", True),
            semantic_overlap_tokens=all_settings.get("semantic_overlap_tokens", 50),
            parent_chunk_multiplier=all_settings.get("parent_chunk_multiplier", 2.0),
            use_llm_for_parent_summary=all_settings.get("use_llm_for_parent_summary", False),
            parent_summary_max_length=all_settings.get("parent_summary_max_length", 300),
            hierarchical_threshold_chars=all_settings.get("hierarchical_threshold_chars", 60000),
            semantic_threshold_chars=all_settings.get("semantic_threshold_chars", 12000),
            min_headers_for_semantic=all_settings.get("min_headers_for_semantic", 3)
        )
    
    async def update_settings(self, settings_update: SettingsUpdate) -> SettingsResponse:
        """Update settings."""
        updates = settings_update.model_dump(exclude_unset=True)
        
        if updates:
            await self.settings_repo.set_multiple(updates)
            logger.info("Settings updated", keys=list(updates.keys()))
        
        return await self.get_settings()
