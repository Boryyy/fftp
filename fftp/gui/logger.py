"""
File logging utilities
"""

import logging
from pathlib import Path
from datetime import datetime


def setup_file_logging(log_dir: Path = None) -> logging.Logger:
    """Setup persistent file logging to ~/.fftp/logs/"""
    if log_dir is None:
        log_dir = Path.home() / ".fftp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"fftp_{datetime.now().strftime('%Y%m%d')}.log"
    
    file_logger = logging.getLogger('fftp')
    file_logger.setLevel(logging.INFO)
    file_logger.handlers.clear()
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    file_logger.addHandler(file_handler)
    file_logger.propagate = False
    
    cleanup_old_logs(log_dir)
    
    return file_logger


def cleanup_old_logs(log_dir: Path, keep_days: int = 30):
    """Remove log files older than keep_days"""
    try:
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        for log_file in log_dir.glob("fftp_*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
    except Exception:
        pass
