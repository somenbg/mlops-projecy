"""
Databricks Job Scheduling Service

A comprehensive service for managing Databricks jobs with support for:
- Creating and managing jobs
- Triggering job runs
- Parallel job execution
- Job monitoring and polling
- Error handling and logging
"""

from .databricks_job_scheduler import (
    DatabricksJobScheduler,
    JobConfig,
    JobRun,
    JobState,
    JobResultState
)

from .config import (
    DatabricksConfig,
    JobTemplate,
    NOTEBOOK_JOB_TEMPLATE,
    PYTHON_SCRIPT_JOB_TEMPLATE,
    SPARK_JAR_JOB_TEMPLATE
)

from .exceptions import (
    DatabricksJobSchedulerError,
    JobCreationError,
    JobTriggerError,
    JobRunError,
    ConfigurationError,
    AuthenticationError,
    TimeoutError,
    ConcurrentJobLimitError
)

from .logger import (
    setup_logger,
    log_job_operation,
    log_job_result
)

__version__ = "1.0.0"
__author__ = "MLOps Team"

__all__ = [
    # Main classes
    "DatabricksJobScheduler",
    "JobConfig",
    "JobRun",
    "JobState",
    "JobResultState",
    
    # Configuration
    "DatabricksConfig",
    "JobTemplate",
    "NOTEBOOK_JOB_TEMPLATE",
    "PYTHON_SCRIPT_JOB_TEMPLATE",
    "SPARK_JAR_JOB_TEMPLATE",
    
    # Exceptions
    "DatabricksJobSchedulerError",
    "JobCreationError",
    "JobTriggerError",
    "JobRunError",
    "ConfigurationError",
    "AuthenticationError",
    "TimeoutError",
    "ConcurrentJobLimitError",
    
    # Logging
    "setup_logger",
    "log_job_operation",
    "log_job_result",
]
