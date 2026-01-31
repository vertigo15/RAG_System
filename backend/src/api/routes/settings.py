"""
Settings API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schemas import SettingsUpdate, SettingsResponse
from src.services.settings_service import SettingsService
from src.repositories.settings_repository import SettingsRepository
from src.dependencies import get_db_session
from src.core.logging import get_logger

router = APIRouter(prefix="/settings")
logger = get_logger(__name__)


def get_settings_service(
    db: AsyncSession = Depends(get_db_session)
) -> SettingsService:
    """Get settings service instance."""
    settings_repo = SettingsRepository(db)
    return SettingsService(settings_repo)


@router.get("", response_model=SettingsResponse)
async def get_settings(
    service: SettingsService = Depends(get_settings_service)
):
    """Get current system settings."""
    return await service.get_settings()


@router.put("", response_model=SettingsResponse)
async def update_settings(
    settings_update: SettingsUpdate,
    service: SettingsService = Depends(get_settings_service)
):
    """Update system settings."""
    return await service.update_settings(settings_update)
