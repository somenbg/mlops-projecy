#!/usr/bin/env python3
"""
Script to trigger and track multiple jobs until completion with CLI support
"""

import asyncio
import argparse
import json
import sys
from typing import List, Dict, Any, Optional
from databricks_job_scheduler import DatabricksJobScheduler
from config import DatabricksConfig
from logger import setup_logger


async def track_jobs(job_configs: List[Dict[str, Any]], max_concurrent: int = 2, poll_interval: int = 10, quiet: bool = False):
    """
    Trigger and track multiple jobs until completion
    
    Args:
        job_configs: List of job configurations with job_id and trigger_params
        max_concurrent: Maximum number of concurrent jobs
        poll_interval: Seconds between status checks
        quiet: Suppress progress output
    """
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    job_ids = [config["job_id"] for config in job_configs]
    if not quiet:
        print(f"🚀 Starting to track {len(job_ids)} jobs: {job_ids}")
        print("=" * 60)
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        # Run jobs in parallel
        if not quiet:
            print(f"⚡ Triggering {len(job_ids)} jobs in parallel...")
        results = await scheduler.run_jobs_parallel(
            job_configs,
            max_concurrent=max_concurrent,
            poll_interval=poll_interval
        )
        
        # Display results
        if not quiet:
            print("\n" + "=" * 60)
            print("📊 JOB EXECUTION RESULTS")
            print("=" * 60)
        
        successful_jobs = 0
        failed_jobs = 0
        
        for i, job_run in enumerate(results):
            job_id = job_run.job_id
            run_id = job_run.run_id
            state = job_run.state.value
            result_state = job_run.result_state.value if job_run.result_state else "N/A"
            
            if not quiet:
                print(f"\n🔍 Job {i+1} (ID: {job_id})")
                print(f"   Run ID: {run_id}")
                print(f"   Final State: {state}")
                print(f"   Result State: {result_state}")
                
                if job_run.start_time:
                    print(f"   Start Time: {job_run.start_time}")
                if job_run.end_time:
                    print(f"   End Time: {job_run.end_time}")
                    if job_run.start_time:
                        duration = (job_run.end_time - job_run.start_time).total_seconds()
                        print(f"   Duration: {duration:.2f} seconds")
                
                if job_run.error_message:
                    print(f"   Error: {job_run.error_message}")
                
                if job_run.run_page_url:
                    print(f"   Run Page: {job_run.run_page_url}")
            
            # Count results
            if result_state == "SUCCESS":
                successful_jobs += 1
                if not quiet:
                    print("   ✅ SUCCESS")
            else:
                failed_jobs += 1
                if not quiet:
                    print("   ❌ FAILED")
        
        # Summary
        if not quiet:
            print("\n" + "=" * 60)
            print("📈 SUMMARY")
            print("=" * 60)
            print(f"Total Jobs: {len(results)}")
            print(f"Successful: {successful_jobs} ✅")
            print(f"Failed: {failed_jobs} ❌")
            print(f"Success Rate: {(successful_jobs/len(results)*100):.1f}%")
        
        return results


def parse_job_parameters(param_string: str) -> Dict[str, str]:
    """
    Parse job parameters from string format
    
    Args:
        param_string: Parameters in format "key1=value1,key2=value2"
        
    Returns:
        Dictionary of parameters
    """
    if not param_string:
        return {}
    
    params = {}
    for pair in param_string.split(','):
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[key.strip()] = value.strip()
        else:
            raise ValueError(f"Invalid parameter format: {pair}. Use key=value format.")
    
    return params


def parse_python_params(param_string: str) -> List[str]:
    """
    Parse Python parameters from string format
    
    Args:
        param_string: Parameters in format "arg1,arg2,arg3"
        
    Returns:
        List of parameters
    """
    if not param_string:
        return []
    
    return [param.strip() for param in param_string.split(',')]


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
            if "job_id" not in job_config:
                raise ValueError("Each job configuration must have a 'job_id' field")
            
            # Ensure trigger_params exists
            if "trigger_params" not in job_config:
                job_config["trigger_params"] = {}
            
            job_configs.append(job_config)
        
        return job_configs
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading configuration file: {e}")


def create_job_configs(job_ids: List[int], 
                      notebook_params: Optional[str] = None,
                      python_params: Optional[str] = None,
                      jar_params: Optional[str] = None,
                      python_named_params: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Create job configurations from CLI arguments
    
    Args:
        job_ids: List of job IDs
        notebook_params: Notebook parameters as string
        python_params: Python parameters as string
        jar_params: JAR parameters as string
        python_named_params: Python named parameters as string
        
    Returns:
        List of job configurations
    """
    job_configs = []
    
    for job_id in job_ids:
        trigger_params = {}
        
        if notebook_params:
            trigger_params["notebook_params"] = parse_job_parameters(notebook_params)
        
        if python_params:
            trigger_params["python_params"] = parse_python_params(python_params)
        
        if jar_params:
            trigger_params["jar_params"] = parse_python_params(jar_params)
        
        if python_named_params:
            trigger_params["python_named_params"] = parse_job_parameters(python_named_params)
        
        job_configs.append({
            "job_id": job_id,
            "trigger_params": trigger_params
        })
    
    return job_configs


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Trigger and track multiple Databricks jobs until completion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Track jobs with default settings
  python track_jobs.py 697909345169014 260482705947228
  
  # Track jobs with notebook parameters
  python track_jobs.py 697909345169014 --notebook-params "input_path=/path/to/input,output_path=/path/to/output"
  
  # Track jobs with Python parameters
  python track_jobs.py 697909345169014 --python-params "arg1,arg2,arg3"
  
  # Track jobs with custom concurrency and polling
  python track_jobs.py 697909345169014 260482705947228 --max-concurrent 3 --poll-interval 15
  
  # Track jobs with different parameter types
  python track_jobs.py 697909345169014 --notebook-params "param1=value1" --python-params "arg1,arg2"
  
  # Track jobs from configuration file
  python track_jobs.py --config-file job_configs.json
  
  # Track jobs from config file with custom settings
  python track_jobs.py --config-file job_configs.json --max-concurrent 4 --poll-interval 5
        """
    )
    
    # Job IDs (positional arguments)
    parser.add_argument(
        "job_ids",
        nargs="*",
        type=int,
        help="Job IDs to trigger and track"
    )
    
    # Config file option
    parser.add_argument(
        "--config-file",
        type=str,
        help="JSON configuration file with job definitions"
    )
    
    # Job parameters
    parser.add_argument(
        "--notebook-params",
        type=str,
        help="Notebook parameters in format 'key1=value1,key2=value2'"
    )
    
    parser.add_argument(
        "--python-params",
        type=str,
        help="Python parameters in format 'arg1,arg2,arg3'"
    )
    
    parser.add_argument(
        "--jar-params",
        type=str,
        help="JAR parameters in format 'arg1,arg2,arg3'"
    )
    
    parser.add_argument(
        "--python-named-params",
        type=str,
        help="Python named parameters in format 'key1=value1,key2=value2'"
    )
    
    # Execution settings
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=2,
        help="Maximum number of concurrent jobs (default: 2)"
    )
    
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Polling interval in seconds (default: 10)"
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
    if not args.config_file and not args.job_ids:
        print("Error: Either provide job IDs or use --config-file option")
        return 1
    
    if args.config_file and args.job_ids:
        print("Error: Cannot specify both job IDs and config file. Use one or the other.")
        return 1
    
    if args.max_concurrent < 1:
        print("Error: max-concurrent must be at least 1")
        return 1
    
    if args.poll_interval < 1:
        print("Error: poll-interval must be at least 1")
        return 1
    
    # Check for conflicting parameters
    param_count = sum([
        bool(args.notebook_params),
        bool(args.python_params),
        bool(args.jar_params),
        bool(args.python_named_params)
    ])
    
    if param_count > 1:
        print("Warning: Multiple parameter types specified. All will be applied to all jobs.")
    
    try:
        # Create job configurations
        if args.config_file:
            # Load from configuration file
            job_configs = load_job_configs_from_file(args.config_file)
            
            # Override with CLI parameters if provided
            if any([args.notebook_params, args.python_params, args.jar_params, args.python_named_params]):
                print("Warning: CLI parameters will override file-based configurations")
                for job_config in job_configs:
                    trigger_params = job_config.get("trigger_params", {})
                    
                    if args.notebook_params:
                        trigger_params["notebook_params"] = parse_job_parameters(args.notebook_params)
                    if args.python_params:
                        trigger_params["python_params"] = parse_python_params(args.python_params)
                    if args.jar_params:
                        trigger_params["jar_params"] = parse_python_params(args.jar_params)
                    if args.python_named_params:
                        trigger_params["python_named_params"] = parse_job_parameters(args.python_named_params)
                    
                    job_config["trigger_params"] = trigger_params
        else:
            # Create from CLI arguments
            if not args.job_ids:
                print("Error: No job IDs provided")
                return 1
            
            job_configs = create_job_configs(
                args.job_ids,
                args.notebook_params,
                args.python_params,
                args.jar_params,
                args.python_named_params
            )
        
        if not args.quiet:
            print("🔧 Databricks Job Tracker")
            print("=" * 60)
            
            if args.config_file:
                print(f"Configuration file: {args.config_file}")
                job_ids = [config["job_id"] for config in job_configs]
                print(f"Tracking jobs: {job_ids}")
            else:
                print(f"Tracking jobs: {args.job_ids}")
            
            if param_count > 0:
                print("With parameters:")
                if args.notebook_params:
                    print(f"  Notebook: {args.notebook_params}")
                if args.python_params:
                    print(f"  Python: {args.python_params}")
                if args.jar_params:
                    print(f"  JAR: {args.jar_params}")
                if args.python_named_params:
                    print(f"  Python Named: {args.python_named_params}")
            print("=" * 60)
        
        # Run the tracking
        results = asyncio.run(track_jobs(
            job_configs,
            max_concurrent=args.max_concurrent,
            poll_interval=args.poll_interval,
            quiet=args.quiet
        ))
        
        # Output results
        if args.json_output:
            # JSON output
            json_results = []
            for job_run in results:
                json_results.append({
                    "job_id": job_run.job_id,
                    "run_id": job_run.run_id,
                    "state": job_run.state.value,
                    "result_state": job_run.result_state.value if job_run.result_state else None,
                    "start_time": job_run.start_time.isoformat() if job_run.start_time else None,
                    "end_time": job_run.end_time.isoformat() if job_run.end_time else None,
                    "duration_seconds": (job_run.end_time - job_run.start_time).total_seconds() if job_run.start_time and job_run.end_time else None,
                    "error_message": job_run.error_message,
                    "run_page_url": job_run.run_page_url,
                    "success": job_run.result_state and job_run.result_state.value == "SUCCESS"
                })
            
            print(json.dumps(json_results, indent=2))
        else:
            # Check if all jobs completed successfully
            all_successful = all(
                job_run.result_state and job_run.result_state.value == "SUCCESS" 
                for job_run in results
            )
            
            if all_successful:
                if not args.quiet:
                    print("\n🎉 All jobs completed successfully!")
            else:
                if not args.quiet:
                    print("\n⚠️  Some jobs failed. Check the details above.")
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
