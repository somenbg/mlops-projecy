#!/usr/bin/env python3
"""
Helper script for listing Databricks jobs, filtering by name, and generating track_jobs configurations
"""

import asyncio
import argparse
import json
import sys
from typing import List, Dict, Any, Optional
from databricks_job_scheduler import DatabricksJobScheduler
from config import DatabricksConfig
from logger import setup_logger


async def list_jobs(scheduler: DatabricksJobScheduler, name_filter: Optional[str] = None, limit: int = 100, offset: int = 0):
    """
    List Databricks jobs with optional name filtering
    
    Args:
        scheduler: DatabricksJobScheduler instance
        name_filter: Optional name filter (case-insensitive partial match)
        limit: Maximum number of jobs to return
        offset: Offset for pagination
        
    Returns:
        List of job information dictionaries
    """
    try:
        # Get all jobs
        jobs_response = await scheduler._make_request("GET", "list", params={
            "limit": limit,
            "offset": offset
        })
        
        jobs = jobs_response.get("jobs", [])
        
        # Filter by name if specified
        if name_filter:
            filtered_jobs = []
            name_filter_lower = name_filter.lower()
            for job in jobs:
                job_name = job.get("settings", {}).get("name", "").lower()
                if name_filter_lower in job_name:
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        return jobs
        
    except Exception as e:
        print(f"Error listing jobs: {e}")
        return []


async def get_job_details(scheduler: DatabricksJobScheduler, job_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed job information including parameters
    
    Args:
        scheduler: DatabricksJobScheduler instance
        job_id: Job ID to get details for
        
    Returns:
        Detailed job information dictionary or None if error
    """
    try:
        job_details = await scheduler._make_request("GET", f"get?job_id={job_id}")
        return job_details
    except Exception as e:
        print(f"Error getting job details for {job_id}: {e}")
        return None


def extract_job_parameters(job_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract existing job parameters from job details
    
    Args:
        job_details: Detailed job information from API
        
    Returns:
        Dictionary of existing job parameters
    """
    if not job_details:
        return {}
    
    settings = job_details.get("settings", {})
    parameters = {}
    
    # Extract job-level parameters (job_parameters)
    if "parameters" in settings and settings["parameters"]:
        parameters["job_parameters"] = settings["parameters"]
    
    # Extract task-level parameters
    tasks = settings.get("tasks", [])
    if not tasks:
        return parameters
    
    # Get the first task (most jobs have one task)
    task = tasks[0]
    
    # Extract notebook parameters
    if "notebook_task" in task:
        notebook_task = task["notebook_task"]
        if "base_parameters" in notebook_task and notebook_task["base_parameters"]:
            parameters["notebook_params"] = notebook_task["base_parameters"]
    
    # Extract Python script parameters
    if "python_script_task" in task:
        python_task = task["python_script_task"]
        if "parameters" in python_task and python_task["parameters"]:
            parameters["python_params"] = python_task["parameters"]
    
    # Extract Spark Python parameters
    if "spark_python_task" in task:
        spark_python_task = task["spark_python_task"]
        if "parameters" in spark_python_task and spark_python_task["parameters"]:
            parameters["python_params"] = spark_python_task["parameters"]
    
    # Extract Spark JAR parameters
    if "spark_jar_task" in task:
        spark_jar_task = task["spark_jar_task"]
        if "parameters" in spark_jar_task and spark_jar_task["parameters"]:
            parameters["jar_params"] = spark_jar_task["parameters"]
    
    # Extract Spark submit parameters
    if "spark_submit_task" in task:
        spark_submit_task = task["spark_submit_task"]
        if "parameters" in spark_submit_task and spark_submit_task["parameters"]:
            parameters["jar_params"] = spark_submit_task["parameters"]
    
    return parameters


def format_job_info(job: Dict[str, Any], show_details: bool = False) -> str:
    """
    Format job information for display
    
    Args:
        job: Job dictionary from API
        show_details: Whether to show detailed information
        
    Returns:
        Formatted string
    """
    job_id = job.get("job_id", "N/A")
    job_name = job.get("settings", {}).get("name", "N/A")
    created_time = job.get("created_time", 0)
    creator = job.get("creator_user_name", "N/A")
    
    # Format creation time
    if created_time > 0:
        from datetime import datetime
        created_dt = datetime.fromtimestamp(created_time / 1000)
        created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        created_str = "N/A"
    
    # Basic info
    info = f"ID: {job_id} | Name: {job_name} | Created: {created_str} | Creator: {creator}"
    
    if show_details:
        # Add more details
        settings = job.get("settings", {})
        timeout = settings.get("timeout_seconds", 0)
        max_retries = settings.get("max_retries", 0)
        max_concurrent = settings.get("max_concurrent_runs", 1)
        
        # Get task type from tasks array
        task_type = "Unknown"
        tasks = settings.get("tasks", [])
        if tasks:
            task = tasks[0]  # Get first task
            if "notebook_task" in task:
                task_type = "Notebook"
            elif "python_script_task" in task:
                task_type = "Python Script"
            elif "spark_jar_task" in task:
                task_type = "Spark JAR"
            elif "spark_python_task" in task:
                task_type = "Spark Python"
            elif "spark_submit_task" in task:
                task_type = "Spark Submit"
        
        # Get cluster info from tasks array
        cluster_info = "Unknown"
        if tasks:
            task = tasks[0]  # Get first task
            if "new_cluster" in task:
                cluster_info = "New Cluster"
            elif "existing_cluster_id" in task:
                cluster_info = f"Existing Cluster: {task['existing_cluster_id']}"
            elif "compute" in task:
                cluster_info = "Serverless Compute"
        
        info += f"\n  Type: {task_type} | Cluster: {cluster_info} | Timeout: {timeout}s | Retries: {max_retries} | Max Concurrent: {max_concurrent}"
        
        # Add tags if available
        tags = settings.get("tags", {})
        if tags:
            tag_str = ", ".join([f"{k}={v}" for k, v in tags.items()])
            info += f"\n  Tags: {tag_str}"
    
    return info


async def get_jobs_with_parameters(scheduler: DatabricksJobScheduler, selected_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get detailed job information including existing parameters for selected jobs
    
    Args:
        scheduler: DatabricksJobScheduler instance
        selected_jobs: List of selected job dictionaries
        
    Returns:
        List of job dictionaries with detailed information and parameters
    """
    jobs_with_params = []
    
    for job in selected_jobs:
        job_id = job["job_id"]
        job_name = job.get("settings", {}).get("name", f"job_{job_id}")
        
        print(f"Getting details for job: {job_name} (ID: {job_id})")
        
        # Get detailed job information
        job_details = await get_job_details(scheduler, job_id)
        
        if job_details:
            # Extract existing parameters
            existing_params = extract_job_parameters(job_details)
            
            # Create enhanced job info
            enhanced_job = {
                "job_id": job_id,
                "name": job_name,
                "existing_params": existing_params,
                "job_details": job_details
            }
            jobs_with_params.append(enhanced_job)
        else:
            # Fallback to basic job info if details can't be retrieved
            enhanced_job = {
                "job_id": job_id,
                "name": job_name,
                "existing_params": {},
                "job_details": None
            }
            jobs_with_params.append(enhanced_job)
    
    return jobs_with_params


def create_track_jobs_config(jobs_with_params: List[Dict[str, Any]], default_params: Optional[Dict[str, Any]] = None, use_existing_params: bool = True) -> Dict[str, Any]:
    """
    Create a track_jobs configuration from jobs with parameters
    
    Args:
        jobs_with_params: List of job dictionaries with parameter information
        default_params: Optional default trigger parameters for all jobs
        use_existing_params: Whether to include existing job parameters
        
    Returns:
        Configuration dictionary for track_jobs
    """
    if len(jobs_with_params) == 1:
        # Single job configuration
        job = jobs_with_params[0]
        
        # Start with existing parameters if available and requested
        trigger_params = {}
        if use_existing_params and job.get("existing_params"):
            trigger_params.update(job["existing_params"])
        
        # Override with default parameters if provided
        if default_params:
            trigger_params.update(default_params)
        
        config = {
            "job_id": job["job_id"],
            "trigger_params": trigger_params
        }
    else:
        # Multiple jobs configuration
        config = []
        for job in jobs_with_params:
            # Start with existing parameters if available and requested
            trigger_params = {}
            if use_existing_params and job.get("existing_params"):
                trigger_params.update(job["existing_params"])
            
            # Override with default parameters if provided
            if default_params:
                trigger_params.update(default_params)
            
            job_config = {
                "job_id": job["job_id"],
                "trigger_params": trigger_params
            }
            config.append(job_config)
    
    return config


def interactive_job_selection(jobs: List[Dict[str, Any]], show_details: bool = False) -> List[Dict[str, Any]]:
    """
    Interactive job selection interface
    
    Args:
        jobs: List of job dictionaries
        show_details: Whether to show detailed information
        
    Returns:
        List of selected job dictionaries
    """
    if not jobs:
        print("No jobs found matching the criteria.")
        return []
    
    print(f"\nFound {len(jobs)} jobs:")
    print("=" * 80)
    
    for i, job in enumerate(jobs, 1):
        print(f"{i:2d}. {format_job_info(job, show_details)}")
    
    print("\nSelect jobs to track (comma-separated numbers, e.g., 1,3,5 or 'all' for all jobs):")
    
    while True:
        try:
            selection = input("Selection: ").strip()
            
            if selection.lower() == 'all':
                return jobs
            
            # Parse selection
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            
            # Validate indices
            if any(i < 0 or i >= len(jobs) for i in indices):
                print("Invalid selection. Please enter valid job numbers.")
                continue
            
            selected_jobs = [jobs[i] for i in indices]
            return selected_jobs
            
        except ValueError:
            print("Invalid input. Please enter comma-separated numbers or 'all'.")
        except KeyboardInterrupt:
            print("\nSelection cancelled.")
            return []


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Helper for listing Databricks jobs and generating track_jobs configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all jobs
  python job_helper.py list
  
  # List jobs with name filter
  python job_helper.py list --name-filter "etl"
  
  # List jobs with details
  python job_helper.py list --name-filter "ml" --details
  
  # Interactive selection and config generation
  python job_helper.py select --name-filter "data"
  
  # Generate config for specific job IDs
  python job_helper.py config --job-ids 123,456,789
  
  # Generate config with default parameters
  python job_helper.py config --job-ids 123,456 --default-params '{"notebook_params": {"env": "prod"}}'
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List jobs')
    list_parser.add_argument('--name-filter', type=str, help='Filter jobs by name (case-insensitive)')
    list_parser.add_argument('--details', action='store_true', help='Show detailed job information')
    list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of jobs to return')
    list_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    list_parser.add_argument('--json-output', action='store_true', help='Output in JSON format')
    
    # Select command
    select_parser = subparsers.add_parser('select', help='Interactive job selection')
    select_parser.add_argument('--name-filter', type=str, help='Filter jobs by name (case-insensitive)')
    select_parser.add_argument('--details', action='store_true', help='Show detailed job information')
    select_parser.add_argument('--limit', type=int, default=100, help='Maximum number of jobs to return')
    select_parser.add_argument('--output-file', type=str, help='Output file for generated config')
    select_parser.add_argument('--default-params', type=str, help='Default trigger parameters as JSON string')
    select_parser.add_argument('--no-existing-params', action='store_true', help='Do not include existing job parameters')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Generate track_jobs configuration')
    config_parser.add_argument('--job-ids', type=str, required=True, help='Comma-separated job IDs')
    config_parser.add_argument('--output-file', type=str, help='Output file for generated config')
    config_parser.add_argument('--default-params', type=str, help='Default trigger parameters as JSON string')
    config_parser.add_argument('--no-existing-params', action='store_true', help='Do not include existing job parameters')
    config_parser.add_argument('--json-output', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize scheduler
        config = DatabricksConfig.from_env()
        logger = setup_logger(level="INFO")
        
        async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
            
            if args.command == 'list':
                # List jobs
                jobs = await list_jobs(
                    scheduler, 
                    name_filter=args.name_filter,
                    limit=args.limit,
                    offset=args.offset
                )
                
                if args.json_output:
                    print(json.dumps(jobs, indent=2))
                else:
                    if not jobs:
                        print("No jobs found matching the criteria.")
                    else:
                        print(f"\nFound {len(jobs)} jobs:")
                        print("=" * 80)
                        for job in jobs:
                            print(format_job_info(job, args.details))
            
            elif args.command == 'select':
                # Interactive selection
                jobs = await list_jobs(
                    scheduler,
                    name_filter=args.name_filter,
                    limit=args.limit,
                    offset=getattr(args, 'offset', 0)
                )
                
                selected_jobs = interactive_job_selection(jobs, args.details)
                
                if selected_jobs:
                    # Parse default parameters if provided
                    default_params = None
                    if args.default_params:
                        try:
                            default_params = json.loads(args.default_params)
                        except json.JSONDecodeError as e:
                            print(f"Error parsing default parameters: {e}")
                            return 1
                    
                    # Get detailed job information with existing parameters
                    print("\nRetrieving job details and existing parameters...")
                    jobs_with_params = await get_jobs_with_parameters(scheduler, selected_jobs)
                    
                    # Generate configuration with existing parameters
                    use_existing = not getattr(args, 'no_existing_params', False)
                    config = create_track_jobs_config(jobs_with_params, default_params, use_existing_params=use_existing)
                    
                    # Output configuration
                    config_json = json.dumps(config, indent=2)
                    
                    if args.output_file:
                        with open(args.output_file, 'w') as f:
                            f.write(config_json)
                        print(f"\nConfiguration saved to: {args.output_file}")
                    else:
                        print(f"\nGenerated track_jobs configuration:")
                        print("=" * 50)
                        print(config_json)
                        
                        print(f"\nTo use this configuration:")
                        print(f"python track_jobs.py --config-file {args.output_file or 'generated_config.json'}")
                else:
                    print("No jobs selected.")
            
            elif args.command == 'config':
                # Generate config for specific job IDs
                job_ids = [int(x.strip()) for x in args.job_ids.split(',')]
                
                # Get job details for the specified IDs
                jobs = await list_jobs(scheduler)
                selected_jobs = [job for job in jobs if job['job_id'] in job_ids]
                
                if not selected_jobs:
                    print("No jobs found with the specified IDs.")
                    return 1
                
                # Parse default parameters if provided
                default_params = None
                if args.default_params:
                    try:
                        default_params = json.loads(args.default_params)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing default parameters: {e}")
                        return 1
                
                # Get detailed job information with existing parameters
                print("Retrieving job details and existing parameters...")
                jobs_with_params = await get_jobs_with_parameters(scheduler, selected_jobs)
                
                # Generate configuration with existing parameters
                use_existing = not getattr(args, 'no_existing_params', False)
                config = create_track_jobs_config(jobs_with_params, default_params, use_existing_params=use_existing)
                
                # Output configuration
                config_json = json.dumps(config, indent=2)
                
                if args.output_file:
                    with open(args.output_file, 'w') as f:
                        f.write(config_json)
                    print(f"Configuration saved to: {args.output_file}")
                else:
                    if args.json_output:
                        print(config_json)
                    else:
                        print("Generated track_jobs configuration:")
                        print("=" * 50)
                        print(config_json)
                        
                        print(f"\nTo use this configuration:")
                        print(f"python track_jobs.py --config-file {args.output_file or 'generated_config.json'}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
