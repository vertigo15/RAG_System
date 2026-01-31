import asyncio
import logging
from core.logging import setup_logging
from consumer import IngestionConsumer

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for ingestion worker"""
    logger.info("Starting RAG System - Ingestion Worker")
    
    consumer = IngestionConsumer()
    
    try:
        await consumer.start()
    except KeyboardInterrupt:
        logger.info("Shutting down ingestion worker")
    except Exception as e:
        logger.error(f"Fatal error in ingestion worker: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
