"""
Example usage of the Databricks Job Scheduling Service

This file demonstrates how to use the service to create, trigger, and monitor
Databricks jobs with parallel execution capabilities.
"""

import asyncio
import os
from databricks_job_scheduler import DatabricksJobScheduler, JobConfig, JobState, JobResultState
from config import DatabricksConfig, NOTEBOOK_JOB_TEMPLATE, PYTHON_SCRIPT_JOB_TEMPLATE
from logger import setup_logger


async def example_single_job():
    """Example: Create and run a single job"""
    print("=== Single Job Example ===")
    
    # Setup configuration
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Create job configuration
    job_config = JobConfig(
        name="example_notebook_job",
        new_cluster={
            "spark_version": "13.3.x-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 2
        },
        notebook_task={
            "notebook_path": "/Users/example@company.com/notebooks/sample_notebook"
        },
        libraries=[
            {"pypi": {"package": "pandas"}},
            {"pypi": {"package": "numpy"}}
        ],
        timeout_seconds=3600,
        max_retries=2
    )
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        # Create the job
        job_id = await scheduler.create_job(job_config)
        print(f"Created job with ID: {job_id}")
        
        # Trigger the job
        run_id = await scheduler.trigger_job(job_id)
        print(f"Triggered job run with ID: {run_id}")
        
        # Wait for completion
        job_run = await scheduler.wait_for_job_completion(run_id)
        print(f"Job completed with state: {job_run.state.value}")
        
        if job_run.result_state:
            print(f"Result state: {job_run.result_state.value}")
        
        if job_run.error_message:
            print(f"Error message: {job_run.error_message}")


async def example_parallel_jobs():
    """Example: Run multiple jobs in parallel"""
    print("\n=== Parallel Jobs Example ===")
    
    # Setup configuration
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Create multiple job configurations
    job_configs = []
    
    # Job 1: Notebook job
    job1_config = JobConfig(
        name="parallel_job_1",
        new_cluster={
            "spark_version": "13.3.x-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 1
        },
        notebook_task={
            "notebook_path": "/Users/example@company.com/notebooks/job1"
        }
    )
    
    # Job 2: Python script job
    job2_config = JobConfig(
        name="parallel_job_2",
        new_cluster={
            "spark_version": "13.3.x-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 1
        },
        python_script_task={
            "python_file": "dbfs:/path/to/script.py"
        }
    )
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        # Create jobs
        job1_id = await scheduler.create_job(job1_config)
        job2_id = await scheduler.create_job(job2_config)
        
        print(f"Created jobs with IDs: {job1_id}, {job2_id}")
        
        # Prepare job configurations for parallel execution
        parallel_jobs = [
            {
                "job_id": job1_id,
                "trigger_params": {
                    "notebook_params": {"param1": "value1", "param2": "value2"}
                }
            },
            {
                "job_id": job2_id,
                "trigger_params": {
                    "python_params": ["arg1", "arg2"]
                }
            }
        ]
        
        # Run jobs in parallel
        results = await scheduler.run_jobs_parallel(
            parallel_jobs,
            max_concurrent=2,
            poll_interval=15
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


async def example_job_management():
    """Example: Job management operations"""
    print("\n=== Job Management Example ===")
    
    # Setup configuration
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        # List all jobs
        jobs = await scheduler.list_jobs(limit=10)
        print(f"Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"  ID: {job['job_id']}, Name: {job['job_name']}")
        
        # Get details of a specific job run
        if jobs:
            # Get the first job's recent runs
            job_id = jobs[0]['job_id']
            print(f"\nGetting details for job {job_id}...")
            
            # Trigger a test run
            run_id = await scheduler.trigger_job(job_id)
            print(f"Triggered test run: {run_id}")
            
            # Get run details
            job_run = await scheduler.get_job_run(run_id)
            print(f"Run details:")
            print(f"  State: {job_run.state.value}")
            print(f"  Start time: {job_run.start_time}")
            if job_run.run_page_url:
                print(f"  Run page URL: {job_run.run_page_url}")


async def example_error_handling():
    """Example: Error handling and recovery"""
    print("\n=== Error Handling Example ===")
    
    try:
        # This will fail if environment variables are not set
        config = DatabricksConfig.from_env()
        
        async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
            # Try to create a job with invalid configuration
            invalid_config = JobConfig(
                name="invalid_job",
                # Missing required task configuration
            )
            
            try:
                job_id = await scheduler.create_job(invalid_config)
            except Exception as e:
                print(f"Expected error when creating invalid job: {e}")
            
            # Try to trigger a non-existent job
            try:
                run_id = await scheduler.trigger_job(999999)  # Non-existent job ID
            except Exception as e:
                print(f"Expected error when triggering non-existent job: {e}")
                
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables")


def main():
    """Run all examples"""
    print("Databricks Job Scheduling Service - Examples")
    print("=" * 50)
    
    # Check if environment variables are set
    if not os.getenv('DATABRICKS_HOST') or not os.getenv('DATABRICKS_TOKEN'):
        print("Please set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables")
        print("You can copy env.example to .env and fill in your values")
        return
    
    # Run examples
    asyncio.run(example_single_job())
    asyncio.run(example_parallel_jobs())
    asyncio.run(example_job_management())
    asyncio.run(example_error_handling())


if __name__ == "__main__":
    main()
