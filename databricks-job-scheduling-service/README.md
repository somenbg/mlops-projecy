# Databricks Job Scheduling Service

A comprehensive Python service for managing Databricks jobs with support for creating, triggering, and monitoring jobs with parallel execution capabilities.

## Features

- **Job Management**: Create, list, and delete Databricks jobs
- **Job Execution**: Trigger individual jobs or run multiple jobs in parallel
- **Job Monitoring**: Poll job status and wait for completion
- **Serverless Compute Support**: Full support for Databricks serverless compute
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
        
        # Create a job (using serverless compute)
        job_config = JobConfig(
            name="my_notebook_job",
            compute=[{"compute_key": "default"}],
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

### Notebook Jobs (Serverless Compute)

```python
job_config = JobConfig(
    name="notebook_job",
    compute=[{"compute_key": "default"}],
    notebook_task={
        "notebook_path": "/path/to/notebook",
        "base_parameters": {"param1": "value1"}
    }
)
```

### Notebook Jobs (Traditional Clusters)

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

### Python Script Jobs (Traditional Cluster)

```python
job_config = JobConfig(
    name="python_script_job",
    new_cluster={
        "spark_version": "15.4.x-scala2.12",
        "node_type_id": "m5d.xlarge",
        "num_workers": 4,
        "spark_conf": {
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.skewJoin.enabled": "true"
        },
        "aws_attributes": {
            "availability": "SPOT",
            "zone_id": "us-west-2a",
            "spot_bid_price_percent": 100,
            "first_on_demand": 1
        },
        "driver_node_type_id": "m5d.xlarge",
        "enable_elastic_disk": True
    },
    python_script_task={
        "python_file": "dbfs:/path/to/script.py"
    },
    libraries=[
        {"pypi": {"package": "pandas==2.0.3"}},
        {"pypi": {"package": "boto3==1.28.25"}}
    ],
    timeout_seconds=3600,
    max_retries=2
)
```

### Spark JAR Jobs (Traditional Cluster)

```python
job_config = JobConfig(
    name="spark_jar_job",
    new_cluster={
        "spark_version": "15.4.x-scala2.12",
        "node_type_id": "c5.2xlarge",
        "num_workers": 6,
        "spark_conf": {
            "spark.sql.adaptive.enabled": "true",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
        },
        "aws_attributes": {
            "availability": "ON_DEMAND",
            "zone_id": "us-west-2a"
        },
        "driver_node_type_id": "c5.2xlarge",
        "enable_elastic_disk": True,
        "init_scripts": [
            {
                "dbfs": {
                    "destination": "dbfs:/init-scripts/spark-setup.sh"
                }
            }
        ]
    },
    spark_jar_task={
        "jar_uri": "dbfs:/path/to/jar.jar",
        "main_class_name": "com.example.MainClass"
    },
    libraries=[
        {"jar": "dbfs:/libraries/aws-sdk.jar"},
        {"maven": {"coordinates": "org.apache.spark:spark-sql_2.12:3.4.0"}}
    ],
    timeout_seconds=10800,
    schedule={
        "quartz_cron_expression": "0 0 2 * * ?",
        "timezone_id": "America/Los_Angeles",
        "pause_status": "UNPAUSED"
    }
)
```

### Existing Cluster Jobs

```python
job_config = JobConfig(
    name="existing_cluster_job",
    existing_cluster_id="1234-567890-cluster123",
    notebook_task={
        "notebook_path": "/path/to/notebook"
    },
    libraries=[
        {"pypi": {"package": "pandas"}},
        {"pypi": {"package": "scikit-learn"}}
    ],
    timeout_seconds=1800
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

## Cluster Configuration Options

### Traditional Cluster Configuration

The service supports comprehensive traditional cluster configurations:

#### Basic Cluster Settings
- `spark_version`: Spark version (e.g., "15.4.x-scala2.12")
- `node_type_id`: Instance type (e.g., "i3.xlarge", "m5d.xlarge", "c5.2xlarge")
- `num_workers`: Number of worker nodes
- `driver_node_type_id`: Driver node type (optional, defaults to worker type)

#### AWS-Specific Settings
- `aws_attributes`: AWS-specific configuration
  - `availability`: "ON_DEMAND" or "SPOT"
  - `zone_id`: Availability zone
  - `spot_bid_price_percent`: Spot instance bid price percentage
  - `first_on_demand`: Number of on-demand instances before using spot

#### Spark Configuration
- `spark_conf`: Spark configuration parameters
  - `spark.sql.adaptive.enabled`: Enable adaptive query execution
  - `spark.serializer`: Serializer class
  - `spark.sql.adaptive.coalescePartitions.enabled`: Enable partition coalescing

#### Additional Features
- `enable_elastic_disk`: Enable automatic disk scaling
- `init_scripts`: Initialization scripts to run on cluster startup
- `custom_tags`: Custom tags for cost tracking and organization

### Serverless Compute Configuration

For serverless compute workspaces:
- `compute`: Array of compute configurations
  - `compute_key`: Compute key (typically "default")

## Examples

See the following example files for comprehensive usage:

### Basic Examples
- `example_usage.py`: General usage examples
- `examples/traditional_cluster_example.py`: Traditional cluster examples

### Configuration Examples
- `examples/notebook_job_config.json`: Serverless notebook job
- `examples/traditional_cluster_notebook_job.json`: Traditional cluster notebook job
- `examples/traditional_cluster_python_job.json`: Traditional cluster Python job
- `examples/traditional_cluster_spark_jar_job.json`: Traditional cluster Spark JAR job
- `examples/traditional_cluster_existing_cluster_job.json`: Existing cluster job

### Advanced Examples
- `examples/parallel_jobs_config.json`: Parallel job execution configuration

## Requirements

- Python 3.7+
- aiohttp >= 3.8.0
- asyncio
- dataclasses
- typing

## License

This project is licensed under the MIT License - see the LICENSE file for details.