import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path is set
from consumer import QueryConsumer

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for query worker"""
    logger.info("Starting RAG System - Query Worker")
    
    consumer = QueryConsumer()
    
    try:
        await consumer.start()
    except KeyboardInterrupt:
        logger.info("Shutting down query worker")
    except Exception as e:
        logger.error(f"Fatal error in query worker: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
