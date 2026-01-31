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
            chunk_overlap=all_settings.get("chunk_overlap", 50)
        )
    
    async def update_settings(self, settings_update: SettingsUpdate) -> SettingsResponse:
        """Update settings."""
        updates = settings_update.model_dump(exclude_unset=True)
        
        if updates:
            await self.settings_repo.set_multiple(updates)
            logger.info("Settings updated", keys=list(updates.keys()))
        
        return await self.get_settings()
