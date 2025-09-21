"""
Configuration module for Databricks Job Scheduling Service
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabricksConfig:
    """Configuration for Databricks connection"""
    host: str
    token: str
    timeout: int = 300
    max_concurrent_jobs: int = 5
    poll_interval: int = 10
    
    @classmethod
    def from_env(cls) -> 'DatabricksConfig':
        """Create configuration from environment variables"""
        host = os.getenv('DATABRICKS_HOST')
        token = os.getenv('DATABRICKS_TOKEN')
        
        if not host:
            raise ValueError("DATABRICKS_HOST environment variable is required")
        if not token:
            raise ValueError("DATABRICKS_TOKEN environment variable is required")
        
        return cls(
            host=host,
            token=token,
            timeout=int(os.getenv('DATABRICKS_TIMEOUT', '300')),
            max_concurrent_jobs=int(os.getenv('DATABRICKS_MAX_CONCURRENT_JOBS', '5')),
            poll_interval=int(os.getenv('DATABRICKS_POLL_INTERVAL', '10'))
        )
    
    @classmethod
    def from_file(cls, config_file: str) -> 'DatabricksConfig':
        """Create configuration from a JSON file"""
        import json
        
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        return cls(
            host=config_data['host'],
            token=config_data['token'],
            timeout=config_data.get('timeout', 300),
            max_concurrent_jobs=config_data.get('max_concurrent_jobs', 5),
            poll_interval=config_data.get('poll_interval', 10)
        )


@dataclass
class JobTemplate:
    """Template for common job configurations"""
    name: str
    cluster_config: dict
    task_config: dict
    libraries: Optional[list] = None
    timeout_seconds: int = 0
    max_retries: int = 0
    tags: Optional[dict] = None


# Common job templates
NOTEBOOK_JOB_TEMPLATE = JobTemplate(
    name="notebook_job_template",
    cluster_config={
        "compute": [{"compute_key": "default"}]
    },
    task_config={
        "notebook_path": "/path/to/notebook"
    },
    libraries=[
        {"pypi": {"package": "pandas"}},
        {"pypi": {"package": "scikit-learn"}}
    ]
)

PYTHON_SCRIPT_JOB_TEMPLATE = JobTemplate(
    name="python_script_job_template",
    cluster_config={
        "compute": [{"compute_key": "default"}]
    },
    task_config={
        "python_file": "dbfs:/path/to/script.py"
    }
)

SPARK_JAR_JOB_TEMPLATE = JobTemplate(
    name="spark_jar_job_template",
    cluster_config={
        "compute": [{"compute_key": "default"}]
    },
    task_config={
        "jar_uri": "dbfs:/path/to/jar.jar",
        "main_class_name": "com.example.MainClass"
    }
)
