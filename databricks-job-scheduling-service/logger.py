"""
Logging configuration for Databricks Job Scheduling Service
"""

import logging
import sys
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str = "databricks_job_scheduler", 
                level: str = "INFO",
                log_file: Optional[str] = None,
                colored: bool = True) -> logging.Logger:
    """
    Setup logger with console and optional file output
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        colored: Whether to use colored output for console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if colored:
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_job_operation(operation: str, job_id: Optional[int] = None, 
                     run_id: Optional[int] = None, **kwargs):
    """
    Log job operations with structured information
    
    Args:
        operation: Operation being performed
        job_id: Job ID (if applicable)
        run_id: Run ID (if applicable)
        **kwargs: Additional context to log
    """
    logger = logging.getLogger("databricks_job_scheduler")
    
    context = {
        "operation": operation,
        "timestamp": datetime.now().isoformat()
    }
    
    if job_id is not None:
        context["job_id"] = job_id
    if run_id is not None:
        context["run_id"] = run_id
    
    context.update(kwargs)
    
    logger.info(f"Job operation: {context}")


def log_job_result(job_run, success: bool = True):
    """
    Log job execution results
    
    Args:
        job_run: JobRun object with execution details
        success: Whether the operation was successful
    """
    logger = logging.getLogger("databricks_job_scheduler")
    
    result_info = {
        "run_id": job_run.run_id,
        "job_id": job_run.job_id,
        "state": job_run.state.value,
        "success": success
    }
    
    if job_run.result_state:
        result_info["result_state"] = job_run.result_state.value
    
    if job_run.start_time:
        result_info["start_time"] = job_run.start_time.isoformat()
    
    if job_run.end_time:
        result_info["end_time"] = job_run.end_time.isoformat()
        if job_run.start_time:
            duration = (job_run.end_time - job_run.start_time).total_seconds()
            result_info["duration_seconds"] = duration
    
    if job_run.error_message:
        result_info["error_message"] = job_run.error_message
    
    if success:
        logger.info(f"Job completed successfully: {result_info}")
    else:
        logger.error(f"Job failed: {result_info}")
