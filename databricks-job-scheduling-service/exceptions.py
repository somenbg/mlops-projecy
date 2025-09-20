"""
Custom exceptions for Databricks Job Scheduling Service
"""


class DatabricksJobSchedulerError(Exception):
    """Base exception for all scheduler errors"""
    pass


class JobCreationError(DatabricksJobSchedulerError):
    """Raised when job creation fails"""
    pass


class JobTriggerError(DatabricksJobSchedulerError):
    """Raised when job triggering fails"""
    pass


class JobRunError(DatabricksJobSchedulerError):
    """Raised when job run operations fail"""
    pass


class ConfigurationError(DatabricksJobSchedulerError):
    """Raised when configuration is invalid"""
    pass


class AuthenticationError(DatabricksJobSchedulerError):
    """Raised when authentication fails"""
    pass


class TimeoutError(DatabricksJobSchedulerError):
    """Raised when operation times out"""
    pass


class ConcurrentJobLimitError(DatabricksJobSchedulerError):
    """Raised when concurrent job limit is exceeded"""
    pass
