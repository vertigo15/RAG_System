"""
Settings repository for key-value storage.
"""

from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.database import Setting
from src.core.logging import get_logger
import json

logger = get_logger(__name__)


class SettingsRepository:
    """Repository for settings operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, key: str) -> Optional[Any]:
        """Get setting by key."""
        result = await self.session.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            return setting.value
        return None
    
    async def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        result = await self.session.execute(select(Setting))
        settings = result.scalars().all()
        return {s.key: s.value for s in settings}
    
    async def set(self, key: str, value: Any, description: Optional[str] = None) -> None:
        """Set setting value."""
        result = await self.session.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = Setting(key=key, value=value, description=description)
            self.session.add(setting)
        
        await self.session.flush()
        logger.info("Setting updated", key=key)
    
    async def set_multiple(self, settings: Dict[str, Any]) -> None:
        """Set multiple settings."""
        for key, value in settings.items():
            await self.set(key, value)
        logger.info("Multiple settings updated", count=len(settings))
