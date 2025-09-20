# Databricks Job Scheduling Service

A comprehensive Python service for managing Databricks jobs with support for creating, triggering, and monitoring jobs with parallel execution capabilities.

## Features

- **Job Management**: Create, list, and delete Databricks jobs
- **Job Execution**: Trigger individual jobs or run multiple jobs in parallel
- **Job Monitoring**: Poll job status and wait for completion
- **Error Handling**: Comprehensive error handling and logging
- **Configuration**: Flexible configuration via environment variables or config files
- **Async Support**: Built with asyncio for efficient concurrent operations

## Installation

1. Clone the repository or copy the service files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your Databricks credentials
   ```

## Quick Start

### Basic Usage

```python
import asyncio
from databricks_job_scheduler import DatabricksJobScheduler, JobConfig

async def main():
    # Initialize the scheduler
    async with DatabricksJobScheduler(
        host="https://your-workspace.cloud.databricks.com",
        token="your_personal_access_token"
    ) as scheduler:
        
        # Create a job
        job_config = JobConfig(
            name="my_notebook_job",
            new_cluster={
                "spark_version": "13.3.x-scala2.12",
                "node_type_id": "i3.xlarge",
                "num_workers": 2
            },
            notebook_task={
                "notebook_path": "/path/to/your/notebook"
            }
        )
        
        job_id = await scheduler.create_job(job_config)
        print(f"Created job with ID: {job_id}")
        
        # Trigger the job
        run_id = await scheduler.trigger_job(job_id)
        print(f"Triggered job run with ID: {run_id}")
        
        # Wait for completion
        job_run = await scheduler.wait_for_job_completion(run_id)
        print(f"Job completed with state: {job_run.state.value}")

# Run the example
asyncio.run(main())
```

### Parallel Job Execution

```python
async def run_parallel_jobs():
    async with DatabricksJobScheduler(host, token) as scheduler:
        # Prepare job configurations
        job_configs = [
            {
                "job_id": job_id_1,
                "trigger_params": {
                    "notebook_params": {"param1": "value1"}
                }
            },
            {
                "job_id": job_id_2,
                "trigger_params": {
                    "python_params": ["arg1", "arg2"]
                }
            }
        ]
        
        # Run jobs in parallel
        results = await scheduler.run_jobs_parallel(
            job_configs,
            max_concurrent=3,
            poll_interval=10
        )
        
        for job_run in results:
            print(f"Job {job_run.job_id} completed: {job_run.state.value}")
```

## Configuration

### Environment Variables

Set the following environment variables:

```bash
# Required
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_personal_access_token

# Optional
DATABRICKS_TIMEOUT=300
DATABRICKS_MAX_CONCURRENT_JOBS=5
DATABRICKS_POLL_INTERVAL=10
```

### Configuration Class

```python
from config import DatabricksConfig

# From environment variables
config = DatabricksConfig.from_env()

# From JSON file
config = DatabricksConfig.from_file("config.json")
```

## API Reference

### DatabricksJobScheduler

Main service class for managing Databricks jobs.

#### Methods

- `create_job(job_config: JobConfig) -> int`: Create a new job
- `trigger_job(job_id: int, **params) -> int`: Trigger a job run
- `get_job_run(run_id: int) -> JobRun`: Get job run details
- `wait_for_job_completion(run_id: int, poll_interval: int = 10) -> JobRun`: Wait for job completion
- `run_jobs_parallel(job_configs: List[Dict], max_concurrent: int = 5) -> List[JobRun]`: Run multiple jobs in parallel
- `list_jobs(limit: int = 20, offset: int = 0) -> List[Dict]`: List all jobs
- `delete_job(job_id: int) -> None`: Delete a job

### JobConfig

Configuration class for Databricks jobs.

#### Parameters

- `name`: Job name
- `new_cluster`: New cluster configuration
- `existing_cluster_id`: Use existing cluster
- `notebook_task`: Notebook task configuration
- `spark_jar_task`: Spark JAR task configuration
- `python_script_task`: Python script task configuration
- `spark_python_task`: Spark Python task configuration
- `spark_submit_task`: Spark submit task configuration
- `libraries`: List of libraries to install
- `timeout_seconds`: Job timeout in seconds
- `max_retries`: Maximum number of retries
- `tags`: Job tags

### JobRun

Represents a job run instance.

#### Attributes

- `run_id`: Run ID
- `job_id`: Job ID
- `state`: Current job state (PENDING, RUNNING, TERMINATED, etc.)
- `result_state`: Result state (SUCCESS, FAILED, etc.)
- `start_time`: Job start time
- `end_time`: Job end time
- `error_message`: Error message if failed
- `run_page_url`: URL to job run page

## Job Types

### Notebook Jobs

```python
job_config = JobConfig(
    name="notebook_job",
    new_cluster={
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2
    },
    notebook_task={
        "notebook_path": "/path/to/notebook",
        "base_parameters": {"param1": "value1"}
    }
)
```

### Python Script Jobs

```python
job_config = JobConfig(
    name="python_script_job",
    new_cluster={
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 1
    },
    python_script_task={
        "python_file": "dbfs:/path/to/script.py"
    }
)
```

### Spark JAR Jobs

```python
job_config = JobConfig(
    name="spark_jar_job",
    new_cluster={
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2
    },
    spark_jar_task={
        "jar_uri": "dbfs:/path/to/jar.jar",
        "main_class_name": "com.example.MainClass"
    }
)
```

## Error Handling

The service includes comprehensive error handling with custom exceptions:

- `DatabricksJobSchedulerError`: Base exception
- `JobCreationError`: Job creation failures
- `JobTriggerError`: Job triggering failures
- `JobRunError`: Job run operation failures
- `ConfigurationError`: Configuration errors
- `AuthenticationError`: Authentication failures
- `TimeoutError`: Operation timeouts

## Logging

The service includes structured logging with colored console output:

```python
from logger import setup_logger

# Setup logger
logger = setup_logger(
    name="my_scheduler",
    level="INFO",
    log_file="scheduler.log",
    colored=True
)
```

## Examples

See `example_usage.py` for comprehensive examples including:
- Single job execution
- Parallel job execution
- Job management operations
- Error handling scenarios

## Requirements

- Python 3.7+
- aiohttp >= 3.8.0
- asyncio
- dataclasses
- typing

## License

This project is licensed under the MIT License - see the LICENSE file for details.