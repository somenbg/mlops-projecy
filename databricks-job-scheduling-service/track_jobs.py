#!/usr/bin/env python3
"""
Script to trigger and track multiple jobs until completion
"""

import asyncio
import logging
from databricks_job_scheduler import DatabricksJobScheduler
from config import DatabricksConfig
from logger import setup_logger


async def track_jobs(job_ids, max_concurrent=2, poll_interval=10):
    """
    Trigger and track multiple jobs until completion
    
    Args:
        job_ids: List of job IDs to trigger and track
        max_concurrent: Maximum number of concurrent jobs
        poll_interval: Seconds between status checks
    """
    config = DatabricksConfig.from_env()
    logger = setup_logger(level="INFO")
    
    print(f"🚀 Starting to track {len(job_ids)} jobs: {job_ids}")
    print("=" * 60)
    
    async with DatabricksJobScheduler(config.host, config.token, config.timeout) as scheduler:
        # Prepare job configurations for parallel execution
        job_configs = []
        for job_id in job_ids:
            job_configs.append({
                "job_id": job_id,
                "trigger_params": {}  # No additional parameters
            })
        
        # Run jobs in parallel
        print(f"⚡ Triggering {len(job_ids)} jobs in parallel...")
        results = await scheduler.run_jobs_parallel(
            job_configs,
            max_concurrent=max_concurrent,
            poll_interval=poll_interval
        )
        
        # Display results
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
                print("   ✅ SUCCESS")
            else:
                failed_jobs += 1
                print("   ❌ FAILED")
        
        # Summary
        print("\n" + "=" * 60)
        print("📈 SUMMARY")
        print("=" * 60)
        print(f"Total Jobs: {len(results)}")
        print(f"Successful: {successful_jobs} ✅")
        print(f"Failed: {failed_jobs} ❌")
        print(f"Success Rate: {(successful_jobs/len(results)*100):.1f}%")
        
        return results


async def main():
    """Main function"""
    # Job IDs to track
    job_ids = [697909345169014, 260482705947228]
    
    print("🔧 Databricks Job Tracker")
    print("=" * 60)
    print(f"Tracking jobs: {job_ids}")
    print("=" * 60)
    
    try:
        results = await track_jobs(job_ids, max_concurrent=2, poll_interval=10)
        
        # Check if all jobs completed successfully
        all_successful = all(
            job_run.result_state and job_run.result_state.value == "SUCCESS" 
            for job_run in results
        )
        
        if all_successful:
            print("\n🎉 All jobs completed successfully!")
        else:
            print("\n⚠️  Some jobs failed. Check the details above.")
            
    except Exception as e:
        print(f"\n💥 Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
