#!/usr/bin/env python3
"""
Command Line Interface for Databricks Job Scheduling Service
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any
from databricks_job_scheduler import DatabricksJobScheduler, JobConfig
from config import DatabricksConfig
from logger import setup_logger


async def create_job_command(args):
    """Create a new job"""
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Load job configuration from file
    with open(args.config_file, 'r') as f:
        job_data = json.load(f)
    
    job_config = JobConfig(**job_data)
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        job_id = await scheduler.create_job(job_config)
        print(f"Created job with ID: {job_id}")


async def trigger_job_command(args):
    """Trigger a job"""
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        run_id = await scheduler.trigger_job(args.job_id)
        print(f"Triggered job run with ID: {run_id}")
        
        if args.wait:
            print("Waiting for job completion...")
            job_run = await scheduler.wait_for_job_completion(run_id, args.poll_interval)
            print(f"Job completed with state: {job_run.state.value}")
            if job_run.result_state:
                print(f"Result state: {job_run.result_state.value}")


async def list_jobs_command(args):
    """List all jobs"""
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        jobs = await scheduler.list_jobs(limit=args.limit, offset=args.offset)
        
        print(f"Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"  ID: {job['job_id']}, Name: {job.get('settings', {}).get('name', 'N/A')}, Created: {job.get('created_time', 'N/A')}")


async def get_job_run_command(args):
    """Get job run details"""
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        job_run = await scheduler.get_job_run(args.run_id)
        
        print(f"Job Run Details:")
        print(f"  Run ID: {job_run.run_id}")
        print(f"  Job ID: {job_run.job_id}")
        print(f"  State: {job_run.state.value}")
        if job_run.result_state:
            print(f"  Result State: {job_run.result_state.value}")
        if job_run.start_time:
            print(f"  Start Time: {job_run.start_time}")
        if job_run.end_time:
            print(f"  End Time: {job_run.end_time}")
        if job_run.error_message:
            print(f"  Error Message: {job_run.error_message}")
        if job_run.run_page_url:
            print(f"  Run Page URL: {job_run.run_page_url}")


async def run_parallel_command(args):
    """Run multiple jobs in parallel"""
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    # Load job configurations from file
    with open(args.config_file, 'r') as f:
        job_configs = json.load(f)
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        results = await scheduler.run_jobs_parallel(
            job_configs,
            max_concurrent=args.max_concurrent,
            poll_interval=args.poll_interval
        )
        
        print(f"Completed {len(results)} jobs:")
        for i, job_run in enumerate(results):
            print(f"  Job {i+1}: ID {job_run.job_id}, State: {job_run.state.value}")
            if job_run.result_state:
                print(f"    Result: {job_run.result_state.value}")


async def delete_job_command(args):
    """Delete a job"""
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        await scheduler.delete_job(args.job_id)
        print(f"Deleted job with ID: {args.job_id}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Databricks Job Scheduling Service CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create job command
    create_parser = subparsers.add_parser("create", help="Create a new job")
    create_parser.add_argument("config_file", help="JSON file with job configuration")
    create_parser.set_defaults(func=create_job_command)
    
    # Trigger job command
    trigger_parser = subparsers.add_parser("trigger", help="Trigger a job")
    trigger_parser.add_argument("job_id", type=int, help="Job ID to trigger")
    trigger_parser.add_argument("--wait", action="store_true", help="Wait for job completion")
    trigger_parser.add_argument("--poll-interval", type=int, default=10, help="Polling interval in seconds")
    trigger_parser.set_defaults(func=trigger_job_command)
    
    # List jobs command
    list_parser = subparsers.add_parser("list", help="List all jobs")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of jobs to list")
    list_parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")
    list_parser.set_defaults(func=list_jobs_command)
    
    # Get job run command
    get_run_parser = subparsers.add_parser("get-run", help="Get job run details")
    get_run_parser.add_argument("run_id", type=int, help="Run ID to get details for")
    get_run_parser.set_defaults(func=get_job_run_command)
    
    # Run parallel command
    parallel_parser = subparsers.add_parser("run-parallel", help="Run multiple jobs in parallel")
    parallel_parser.add_argument("config_file", help="JSON file with job configurations")
    parallel_parser.add_argument("--max-concurrent", type=int, default=5, help="Maximum concurrent jobs")
    parallel_parser.add_argument("--poll-interval", type=int, default=10, help="Polling interval in seconds")
    parallel_parser.set_defaults(func=run_parallel_command)
    
    # Delete job command
    delete_parser = subparsers.add_parser("delete", help="Delete a job")
    delete_parser.add_argument("job_id", type=int, help="Job ID to delete")
    delete_parser.set_defaults(func=delete_job_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Check for required environment variables
    if not DatabricksConfig.from_env().host or not DatabricksConfig.from_env().token:
        print("Error: DATABRICKS_HOST and DATABRICKS_TOKEN environment variables are required")
        print("Please set them or copy env.example to .env and fill in your values")
        sys.exit(1)
    
    # Run the command
    try:
        asyncio.run(args.func(args))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
