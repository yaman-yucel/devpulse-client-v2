import sys
from datetime import datetime
from pathlib import Path

from loguru import logger


def setup_logging() -> None:
    

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"devpulse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger.remove()  # Remove default logger
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        backtrace=True,
        diagnose=True,
        enqueue=True,
        colorize=True,
    )
    # File logging with rotation, retention, compression
    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        backtrace=True,
        diagnose=True,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        enqueue=True,
        encoding="utf-8",
    )
