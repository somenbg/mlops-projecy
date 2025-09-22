#!/usr/bin/env python3
"""
Script to create Databricks jobs from command line and configuration files
"""

import asyncio
import argparse
import json
import sys
from typing import List, Dict, Any, Optional
from databricks_job_scheduler import DatabricksJobScheduler, JobConfig
from config import DatabricksConfig
from logger import setup_logger


async def create_jobs(job_configs: List[Dict[str, Any]], quiet: bool = False):
    """
    Create multiple Databricks jobs
    
    Args:
        job_configs: List of job configurations
        quiet: Suppress progress output
    """
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    if not quiet:
        print(f"🚀 Creating {len(job_configs)} jobs...")
        print("=" * 60)
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        created_jobs = []
        failed_jobs = []
        
        for i, job_config_dict in enumerate(job_configs):
            try:
                # Convert dict to JobConfig object
                job_config = JobConfig(**job_config_dict)
                
                if not quiet:
                    print(f"Creating job {i+1}/{len(job_configs)}: {job_config.name}")
                
                # Create the job
                job_id = await scheduler.create_job(job_config)
                
                created_jobs.append({
                    "name": job_config.name,
                    "job_id": job_id,
                    "config": job_config_dict
                })
                
                if not quiet:
                    print(f"  ✅ Created job '{job_config.name}' with ID: {job_id}")
                
            except Exception as e:
                error_info = {
                    "name": job_config_dict.get("name", f"job_{i+1}"),
                    "error": str(e),
                    "config": job_config_dict
                }
                failed_jobs.append(error_info)
                
                if not quiet:
                    print(f"  ❌ Failed to create job '{job_config_dict.get('name', f'job_{i+1}')}': {e}")
        
        # Display results
        if not quiet:
            print("\n" + "=" * 60)
            print("📊 JOB CREATION RESULTS")
            print("=" * 60)
            
            if created_jobs:
                print(f"\n✅ Successfully created {len(created_jobs)} jobs:")
                for job in created_jobs:
                    print(f"  • {job['name']} (ID: {job['job_id']})")
            
            if failed_jobs:
                print(f"\n❌ Failed to create {len(failed_jobs)} jobs:")
                for job in failed_jobs:
                    print(f"  • {job['name']}: {job['error']}")
            
            print(f"\n📈 SUMMARY")
            print(f"Total jobs: {len(job_configs)}")
            print(f"Created: {len(created_jobs)} ✅")
            print(f"Failed: {len(failed_jobs)} ❌")
            print(f"Success Rate: {(len(created_jobs)/len(job_configs)*100):.1f}%")
        
        return {
            "created_jobs": created_jobs,
            "failed_jobs": failed_jobs,
            "total_jobs": len(job_configs),
            "success_count": len(created_jobs),
            "failure_count": len(failed_jobs)
        }


def load_job_configs_from_file(config_file: str) -> List[Dict[str, Any]]:
    """
    Load job configurations from a JSON file
    
    Args:
        config_file: Path to JSON configuration file
        
    Returns:
        List of job configurations
    """
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Handle both single job and array of jobs
        if isinstance(config_data, dict):
            config_data = [config_data]
        
        job_configs = []
        for job_config in config_data:
            # Validate required fields
            if "name" not in job_config:
                raise ValueError("Each job configuration must have a 'name' field")
            
            job_configs.append(job_config)
        
        return job_configs
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading configuration file: {e}")


def create_job_config_from_args(args) -> Dict[str, Any]:
    """
    Create a job configuration from CLI arguments
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Job configuration dictionary
    """
    job_config = {
        "name": args.name,
        "max_concurrent_runs": args.max_concurrent_runs,
        "timeout_seconds": args.timeout_seconds,
        "max_retries": args.max_retries,
        "retry_on_timeout": args.retry_on_timeout
    }
    
    # Add cluster configuration
    if args.new_cluster:
        job_config["new_cluster"] = json.loads(args.new_cluster)
    elif args.existing_cluster_id:
        job_config["existing_cluster_id"] = args.existing_cluster_id
    elif args.compute:
        job_config["compute"] = json.loads(args.compute)
    
    # Add task configuration
    if args.notebook_task:
        job_config["notebook_task"] = json.loads(args.notebook_task)
    elif args.python_script_task:
        job_config["python_script_task"] = json.loads(args.python_script_task)
    elif args.spark_jar_task:
        job_config["spark_jar_task"] = json.loads(args.spark_jar_task)
    elif args.spark_python_task:
        job_config["spark_python_task"] = json.loads(args.spark_python_task)
    elif args.spark_submit_task:
        job_config["spark_submit_task"] = json.loads(args.spark_submit_task)
    
    # Add optional configurations
    if args.libraries:
        job_config["libraries"] = json.loads(args.libraries)
    if args.email_notifications:
        job_config["email_notifications"] = json.loads(args.email_notifications)
    if args.schedule:
        job_config["schedule"] = json.loads(args.schedule)
    if args.tags:
        job_config["tags"] = json.loads(args.tags)
    
    return job_config


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Create Databricks jobs from command line or configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a single job from CLI arguments
  python create_jobs.py --name "my_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --new-cluster '{"spark_version": "15.4.x-scala2.12", "node_type_id": "i3.xlarge", "num_workers": 2}'
  
  # Create jobs from configuration file
  python create_jobs.py --config-file job_configs.json
  
  # Create serverless job
  python create_jobs.py --name "serverless_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --compute '[{"compute_key": "default"}]'
  
  # Create job with all parameters
  python create_jobs.py --name "complex_job" --notebook-task '{"notebook_path": "/path/to/notebook", "base_parameters": {"param1": "value1"}}' --new-cluster '{"spark_version": "15.4.x-scala2.12", "node_type_id": "i3.xlarge", "num_workers": 2}' --libraries '[{"pypi": {"package": "pandas"}}]' --tags '{"environment": "production"}'
        """
    )
    
    # Configuration source (mutually exclusive)
    config_group = parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument(
        "--config-file",
        type=str,
        help="JSON configuration file with job definitions"
    )
    config_group.add_argument(
        "--name",
        type=str,
        help="Job name (required when not using config file)"
    )
    
    # Cluster configuration (mutually exclusive)
    cluster_group = parser.add_mutually_exclusive_group()
    cluster_group.add_argument(
        "--new-cluster",
        type=str,
        help="New cluster configuration as JSON string"
    )
    cluster_group.add_argument(
        "--existing-cluster-id",
        type=str,
        help="Existing cluster ID"
    )
    cluster_group.add_argument(
        "--compute",
        type=str,
        help="Serverless compute configuration as JSON string"
    )
    
    # Task configuration (mutually exclusive)
    task_group = parser.add_mutually_exclusive_group()
    task_group.add_argument(
        "--notebook-task",
        type=str,
        help="Notebook task configuration as JSON string"
    )
    task_group.add_argument(
        "--python-script-task",
        type=str,
        help="Python script task configuration as JSON string"
    )
    task_group.add_argument(
        "--spark-jar-task",
        type=str,
        help="Spark JAR task configuration as JSON string"
    )
    task_group.add_argument(
        "--spark-python-task",
        type=str,
        help="Spark Python task configuration as JSON string"
    )
    task_group.add_argument(
        "--spark-submit-task",
        type=str,
        help="Spark submit task configuration as JSON string"
    )
    
    # Optional configurations
    parser.add_argument(
        "--libraries",
        type=str,
        help="Libraries configuration as JSON string"
    )
    parser.add_argument(
        "--email-notifications",
        type=str,
        help="Email notifications configuration as JSON string"
    )
    parser.add_argument(
        "--schedule",
        type=str,
        help="Schedule configuration as JSON string"
    )
    parser.add_argument(
        "--tags",
        type=str,
        help="Tags configuration as JSON string"
    )
    
    # Job settings
    parser.add_argument(
        "--max-concurrent-runs",
        type=int,
        default=1,
        help="Maximum concurrent runs (default: 1)"
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=0,
        help="Job timeout in seconds (default: 0 - no timeout)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=0,
        help="Maximum number of retries (default: 0)"
    )
    parser.add_argument(
        "--retry-on-timeout",
        action="store_true",
        help="Retry on timeout"
    )
    
    # Output options
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output, only show final results"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.config_file and not args.name:
        print("Error: Either provide --config-file or --name")
        return 1
    
    if args.config_file and args.name:
        print("Error: Cannot specify both --config-file and --name. Use one or the other.")
        return 1
    
    if not args.config_file:
        # Validate required fields for CLI mode
        if not any([args.notebook_task, args.python_script_task, args.spark_jar_task, 
                   args.spark_python_task, args.spark_submit_task]):
            print("Error: Must specify at least one task type (--notebook-task, --python-script-task, etc.)")
            return 1
        
        if not any([args.new_cluster, args.existing_cluster_id, args.compute]):
            print("Error: Must specify cluster configuration (--new-cluster, --existing-cluster-id, or --compute)")
            return 1
    
    try:
        # Create job configurations
        if args.config_file:
            # Load from configuration file
            job_configs = load_job_configs_from_file(args.config_file)
        else:
            # Create from CLI arguments
            job_config = create_job_config_from_args(args)
            job_configs = [job_config]
        
        if not args.quiet:
            print("🔧 Databricks Job Creator")
            print("=" * 60)
            if args.config_file:
                print(f"Configuration file: {args.config_file}")
            else:
                print(f"Job name: {args.name}")
            print("=" * 60)
        
        # Create the jobs
        results = asyncio.run(create_jobs(job_configs, quiet=args.quiet))
        
        # Output results
        if args.json_output:
            # JSON output
            json_results = {
                "created_jobs": results["created_jobs"],
                "failed_jobs": results["failed_jobs"],
                "summary": {
                    "total_jobs": results["total_jobs"],
                    "success_count": results["success_count"],
                    "failure_count": results["failure_count"],
                    "success_rate": (results["success_count"] / results["total_jobs"] * 100) if results["total_jobs"] > 0 else 0
                }
            }
            print(json.dumps(json_results, indent=2))
        else:
            # Check if all jobs were created successfully
            if results["failure_count"] == 0:
                if not args.quiet:
                    print("\n🎉 All jobs created successfully!")
            else:
                if not args.quiet:
                    print(f"\n⚠️  {results['failure_count']} jobs failed to create. Check the details above.")
                return 1
        
        return 0
        
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
