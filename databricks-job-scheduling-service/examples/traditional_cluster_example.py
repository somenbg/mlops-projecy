#!/usr/bin/env python3
"""
Example usage of Databricks Job Scheduling Service with Traditional Clusters

This script demonstrates how to create and manage jobs using traditional
Databricks clusters (non-serverless) with various configurations.
"""

import asyncio
import logging
from databricks_job_scheduler import DatabricksJobScheduler, JobConfig
from config import DatabricksConfig
from logger import setup_logger


async def example_traditional_cluster_notebook_job():
    """Example: Create a notebook job with traditional cluster"""
    print("=== Traditional Cluster Notebook Job Example ===")
    
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Create job configuration with traditional cluster
    job_config = JobConfig(
        name="traditional_notebook_job",
        new_cluster={
            "spark_version": "15.4.x-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 2,
            "spark_conf": {
                "spark.sql.adaptive.enabled": "true",
                "spark.sql.adaptive.coalescePartitions.enabled": "true",
                "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
            },
            "aws_attributes": {
                "availability": "ON_DEMAND",
                "zone_id": "us-west-2a"
            },
            "driver_node_type_id": "i3.xlarge",
            "enable_elastic_disk": True
        },
        notebook_task={
            "notebook_path": "/Users/somenbg@gmail.com/notebooks/traditional_cluster_notebook",
            "base_parameters": {
                "input_path": "/path/to/input",
                "output_path": "/path/to/output",
                "model_version": "v2.0"
            }
        },
        libraries=[
            {"pypi": {"package": "pandas==2.0.3"}},
            {"pypi": {"package": "scikit-learn==1.3.0"}},
            {"pypi": {"package": "numpy==1.24.3"}}
        ],
        timeout_seconds=7200,
        max_retries=3,
        retry_on_timeout=True,
        email_notifications={
            "on_start": ["admin@company.com"],
            "on_success": ["team@company.com"],
            "on_failure": ["admin@company.com", "team@company.com"]
        },
        tags={
            "environment": "production",
            "team": "data-engineering",
            "project": "ml-pipeline"
        }
    )
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        try:
            # Create the job
            job_id = await scheduler.create_job(job_config)
            print(f"Created traditional cluster job with ID: {job_id}")
            
            # Trigger the job
            run_id = await scheduler.trigger_job(job_id)
            print(f"Triggered job run with ID: {run_id}")
            
            # Wait for completion
            job_run = await scheduler.wait_for_job_completion(run_id, poll_interval=15)
            print(f"Job completed with state: {job_run.state.value}")
            
            if job_run.result_state:
                print(f"Result state: {job_run.result_state.value}")
            
            if job_run.error_message:
                print(f"Error message: {job_run.error_message}")
                
        except Exception as e:
            print(f"Error: {e}")


async def example_traditional_cluster_python_job():
    """Example: Create a Python script job with traditional cluster"""
    print("\n=== Traditional Cluster Python Job Example ===")
    
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Create job configuration with spot instances for cost optimization
    job_config = JobConfig(
        name="traditional_python_job",
        new_cluster={
            "spark_version": "15.4.x-scala2.12",
            "node_type_id": "m5d.xlarge",
            "num_workers": 4,
            "spark_conf": {
                "spark.sql.adaptive.enabled": "true",
                "spark.sql.adaptive.skewJoin.enabled": "true",
                "spark.sql.adaptive.localShuffleReader.enabled": "true"
            },
            "aws_attributes": {
                "availability": "SPOT",
                "zone_id": "us-west-2a",
                "spot_bid_price_percent": 100,
                "first_on_demand": 1
            },
            "driver_node_type_id": "m5d.xlarge",
            "enable_elastic_disk": True,
            "custom_tags": {
                "Environment": "production",
                "Owner": "data-team"
            }
        },
        python_script_task={
            "python_file": "dbfs:/scripts/data_processing.py"
        },
        libraries=[
            {"pypi": {"package": "requests==2.31.0"}},
            {"pypi": {"package": "boto3==1.28.25"}},
            {"pypi": {"package": "pandas==2.0.3"}},
            {"pypi": {"package": "pyarrow==12.0.1"}}
        ],
        timeout_seconds=3600,
        max_retries=2,
        retry_on_timeout=True,
        tags={
            "environment": "production",
            "team": "data-engineering",
            "workload": "etl"
        }
    )
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        try:
            # Create the job
            job_id = await scheduler.create_job(job_config)
            print(f"Created Python job with ID: {job_id}")
            
            # Trigger the job with parameters
            run_id = await scheduler.trigger_job(
                job_id,
                python_params=[
                    "--input-path", "/path/to/input",
                    "--output-path", "/path/to/output",
                    "--batch-size", "10000"
                ]
            )
            print(f"Triggered job run with ID: {run_id}")
            
        except Exception as e:
            print(f"Error: {e}")


async def example_traditional_cluster_spark_jar_job():
    """Example: Create a Spark JAR job with traditional cluster"""
    print("\n=== Traditional Cluster Spark JAR Job Example ===")
    
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Create job configuration for Spark JAR
    job_config = JobConfig(
        name="traditional_spark_jar_job",
        new_cluster={
            "spark_version": "15.4.x-scala2.12",
            "node_type_id": "c5.2xlarge",
            "num_workers": 6,
            "spark_conf": {
                "spark.sql.adaptive.enabled": "true",
                "spark.sql.adaptive.coalescePartitions.enabled": "true",
                "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                "spark.sql.adaptive.skewJoin.enabled": "true"
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
            "jar_uri": "dbfs:/jars/data-processing-app.jar",
            "main_class_name": "com.company.dataprocessing.MainApp"
        },
        libraries=[
            {"jar": "dbfs:/libraries/aws-sdk.jar"},
            {"jar": "dbfs:/libraries/json4s.jar"},
            {"maven": {"coordinates": "org.apache.spark:spark-sql_2.12:3.4.0"}}
        ],
        timeout_seconds=10800,
        max_retries=2,
        retry_on_timeout=True,
        schedule={
            "quartz_cron_expression": "0 0 2 * * ?",
            "timezone_id": "America/Los_Angeles",
            "pause_status": "UNPAUSED"
        },
        tags={
            "environment": "production",
            "team": "spark-engineering",
            "workload": "batch-processing"
        }
    )
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        try:
            # Create the job
            job_id = await scheduler.create_job(job_config)
            print(f"Created Spark JAR job with ID: {job_id}")
            
            # Trigger the job with parameters
            run_id = await scheduler.trigger_job(
                job_id,
                jar_params=[
                    "--input", "/path/to/input",
                    "--output", "/path/to/output",
                    "--config", "/path/to/config.json"
                ]
            )
            print(f"Triggered job run with ID: {run_id}")
            
        except Exception as e:
            print(f"Error: {e}")


async def example_existing_cluster_job():
    """Example: Create a job using an existing cluster"""
    print("\n=== Existing Cluster Job Example ===")
    
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Create job configuration using existing cluster
    job_config = JobConfig(
        name="existing_cluster_job",
        existing_cluster_id="1234-567890-cluster123",  # Replace with actual cluster ID
        notebook_task={
            "notebook_path": "/Users/somenbg@gmail.com/notebooks/existing_cluster_notebook",
            "base_parameters": {
                "input_path": "/path/to/input",
                "output_path": "/path/to/output"
            }
        },
        libraries=[
            {"pypi": {"package": "pandas==2.0.3"}},
            {"pypi": {"package": "scikit-learn==1.3.0"}}
        ],
        timeout_seconds=1800,
        max_retries=1,
        retry_on_timeout=False,
        tags={
            "environment": "development",
            "team": "data-science",
            "cluster": "shared-dev"
        }
    )
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        try:
            # Create the job
            job_id = await scheduler.create_job(job_config)
            print(f"Created existing cluster job with ID: {job_id}")
            
        except Exception as e:
            print(f"Error: {e}")


async def example_parallel_traditional_jobs():
    """Example: Run multiple traditional cluster jobs in parallel"""
    print("\n=== Parallel Traditional Cluster Jobs Example ===")
    
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Create multiple job configurations
    job_configs = []
    
    # Job 1: Notebook job with i3.xlarge
    job1_config = JobConfig(
        name="parallel_notebook_job_1",
        new_cluster={
            "spark_version": "15.4.x-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 2
        },
        notebook_task={
            "notebook_path": "/Users/somenbg@gmail.com/notebooks/job1"
        }
    )
    
    # Job 2: Python job with m5d.xlarge
    job2_config = JobConfig(
        name="parallel_python_job_2",
        new_cluster={
            "spark_version": "15.4.x-scala2.12",
            "node_type_id": "m5d.xlarge",
            "num_workers": 3
        },
        python_script_task={
            "python_file": "dbfs:/scripts/job2.py"
        }
    )
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        try:
            # Create jobs
            job1_id = await scheduler.create_job(job1_config)
            job2_id = await scheduler.create_job(job2_config)
            
            print(f"Created jobs with IDs: {job1_id}, {job2_id}")
            
            # Prepare job configurations for parallel execution
            parallel_jobs = [
                {
                    "job_id": job1_id,
                    "trigger_params": {
                        "notebook_params": {
                            "input_path": "/path/to/input1",
                            "output_path": "/path/to/output1"
                        }
                    }
                },
                {
                    "job_id": job2_id,
                    "trigger_params": {
                        "python_params": [
                            "--input-path", "/path/to/input2",
                            "--output-path", "/path/to/output2"
                        ]
                    }
                }
            ]
            
            # Run jobs in parallel
            results = await scheduler.run_jobs_parallel(
                parallel_jobs,
                max_concurrent=2,
                poll_interval=20
            )
            
            # Print results
            for i, job_run in enumerate(results):
                print(f"Job {i+1} completed:")
                print(f"  Run ID: {job_run.run_id}")
                print(f"  State: {job_run.state.value}")
                if job_run.result_state:
                    print(f"  Result: {job_run.result_state.value}")
                if job_run.error_message:
                    print(f"  Error: {job_run.error_message}")
                print()
                
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Run all traditional cluster examples"""
    print("Databricks Job Scheduling Service - Traditional Cluster Examples")
    print("=" * 70)
    
    # Check if environment variables are set
    import os
    if not os.getenv('DATABRICKS_HOST') or not os.getenv('DATABRICKS_TOKEN'):
        print("Please set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables")
        print("You can copy env.example to .env and fill in your values")
        return
    
    # Run examples
    asyncio.run(example_traditional_cluster_notebook_job())
    asyncio.run(example_traditional_cluster_python_job())
    asyncio.run(example_traditional_cluster_spark_jar_job())
    asyncio.run(example_existing_cluster_job())
    asyncio.run(example_parallel_traditional_jobs())


if __name__ == "__main__":
    main()
