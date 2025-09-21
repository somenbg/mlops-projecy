"""
Databricks Job Scheduling Service

A service that allows users to create, trigger, and monitor Databricks jobs
with support for parallel execution and polling to completion.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import aiohttp
from datetime import datetime


class JobState(Enum):
    """Job execution states"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"
    SKIPPED = "SKIPPED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class JobResultState(Enum):
    """Job result states"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEDOUT = "TIMEDOUT"
    CANCELLED = "CANCELLED"


@dataclass
class JobConfig:
    """Configuration for a Databricks job"""
    name: str
    new_cluster: Optional[Dict[str, Any]] = None
    existing_cluster_id: Optional[str] = None
    compute: Optional[List[Dict[str, Any]]] = None  # For serverless compute
    libraries: Optional[List[Dict[str, Any]]] = None
    notebook_task: Optional[Dict[str, Any]] = None
    spark_jar_task: Optional[Dict[str, Any]] = None
    python_script_task: Optional[Dict[str, Any]] = None
    spark_python_task: Optional[Dict[str, Any]] = None
    spark_submit_task: Optional[Dict[str, Any]] = None
    max_concurrent_runs: int = 1
    timeout_seconds: int = 0
    email_notifications: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None
    max_retries: int = 0
    retry_on_timeout: bool = False
    tags: Optional[Dict[str, str]] = None


@dataclass
class JobRun:
    """Represents a job run instance"""
    run_id: int
    job_id: int
    state: JobState
    result_state: Optional[JobResultState] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    run_page_url: Optional[str] = None


class DatabricksJobScheduler:
    """Main service class for managing Databricks jobs"""
    
    def __init__(self, host: str, token: str, timeout: int = 300):
        """
        Initialize the Databricks Job Scheduler
        
        Args:
            host: Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)
            token: Personal access token or service principal token
            timeout: Default timeout for job execution in seconds
        """
        self.host = host.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.session = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Databricks API"""
        url = f"{self.host}/api/2.1/jobs/{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    self.logger.error(f"HTTP request failed: {response.status}, message='{response.reason}', url={url}")
                    self.logger.error(f"Response body: {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"{response.status}: {response.reason} - {error_text}"
                    )
                return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
    
    async def create_job(self, job_config: JobConfig) -> int:
        """
        Create a new Databricks job
        
        Args:
            job_config: Job configuration
            
        Returns:
            Job ID of the created job
        """
        self.logger.info(f"Creating job: {job_config.name}")
        
        # Prepare job payload according to Databricks API spec
        job_payload = {
            "name": job_config.name,
            "max_concurrent_runs": job_config.max_concurrent_runs,
            "timeout_seconds": job_config.timeout_seconds,
            "max_retries": job_config.max_retries,
            "retry_on_timeout": job_config.retry_on_timeout
        }
        
        # Create tasks array - Databricks API requires tasks array
        tasks = []
        
        # Build task configuration
        task = {}
        
        # Add cluster configuration to task
        if job_config.new_cluster:
            task["new_cluster"] = job_config.new_cluster
        elif job_config.existing_cluster_id:
            task["existing_cluster_id"] = job_config.existing_cluster_id
        elif job_config.compute:
            # For serverless compute, add compute configuration
            task["compute"] = job_config.compute
        
        # Add task type configuration
        if job_config.notebook_task:
            task["notebook_task"] = job_config.notebook_task
        elif job_config.spark_jar_task:
            task["spark_jar_task"] = job_config.spark_jar_task
        elif job_config.python_script_task:
            task["python_script_task"] = job_config.python_script_task
        elif job_config.spark_python_task:
            task["spark_python_task"] = job_config.spark_python_task
        elif job_config.spark_submit_task:
            task["spark_submit_task"] = job_config.spark_submit_task
        
        # Add libraries to task (only for non-serverless compute)
        if job_config.libraries and not job_config.compute:
            task["libraries"] = job_config.libraries
        elif job_config.libraries and job_config.compute:
            # For serverless compute, libraries go in environment
            if "environment" not in task:
                task["environment"] = {}
            task["environment"]["spec"] = {
                "libraries": job_config.libraries
            }
        
        # Add task name (required)
        task["task_key"] = f"{job_config.name}_task"
        
        # Add timeout to task
        if job_config.timeout_seconds > 0:
            task["timeout_seconds"] = job_config.timeout_seconds
        
        tasks.append(task)
        job_payload["tasks"] = tasks
        
        # Add optional job-level configurations
        if job_config.email_notifications:
            job_payload["email_notifications"] = job_config.email_notifications
        if job_config.schedule:
            job_payload["schedule"] = job_config.schedule
        if job_config.tags:
            job_payload["tags"] = job_config.tags
        
        try:
            # Debug logging
            self.logger.debug(f"Job payload: {json.dumps(job_payload, indent=2)}")
            response = await self._make_request("POST", "create", job_payload)
            job_id = response["job_id"]
            self.logger.info(f"Job created successfully with ID: {job_id}")
            return job_id
        except Exception as e:
            self.logger.error(f"Failed to create job: {e}")
            raise
    
    async def trigger_job(self, job_id: int, notebook_params: Optional[Dict[str, str]] = None,
                         python_params: Optional[List[str]] = None,
                         jar_params: Optional[List[str]] = None,
                         python_named_params: Optional[Dict[str, str]] = None) -> int:
        """
        Trigger a job run
        
        Args:
            job_id: ID of the job to run
            notebook_params: Parameters for notebook tasks
            python_params: Parameters for Python tasks
            jar_params: Parameters for JAR tasks
            python_named_params: Named parameters for Python tasks
            
        Returns:
            Run ID of the triggered job
        """
        self.logger.info(f"Triggering job: {job_id}")
        
        run_payload = {"job_id": job_id}
        
        if notebook_params:
            run_payload["notebook_params"] = notebook_params
        if python_params:
            run_payload["python_params"] = python_params
        if jar_params:
            run_payload["jar_params"] = jar_params
        if python_named_params:
            run_payload["python_named_params"] = python_named_params
        
        try:
            response = await self._make_request("POST", "run-now", run_payload)
            run_id = response["run_id"]
            self.logger.info(f"Job triggered successfully with run ID: {run_id}")
            return run_id
        except Exception as e:
            self.logger.error(f"Failed to trigger job: {e}")
            raise
    
    async def get_job_run(self, run_id: int) -> JobRun:
        """
        Get details of a specific job run
        
        Args:
            run_id: Run ID to get details for
            
        Returns:
            JobRun object with run details
        """
        try:
            response = await self._make_request("GET", f"runs/get?run_id={run_id}")
            run_data = response
            
            # Parse job state
            state = JobState(run_data["state"]["life_cycle_state"])
            result_state = None
            if run_data["state"].get("result_state"):
                result_state = JobResultState(run_data["state"]["result_state"])
            
            # Parse timestamps
            start_time = None
            if run_data["start_time"]:
                start_time = datetime.fromtimestamp(run_data["start_time"] / 1000)
            
            end_time = None
            if run_data.get("end_time"):
                end_time = datetime.fromtimestamp(run_data["end_time"] / 1000)
            
            return JobRun(
                run_id=run_data["run_id"],
                job_id=run_data["job_id"],
                state=state,
                result_state=result_state,
                start_time=start_time,
                end_time=end_time,
                error_message=run_data["state"].get("state_message"),
                run_page_url=run_data.get("run_page_url")
            )
        except Exception as e:
            self.logger.error(f"Failed to get job run details: {e}")
            raise
    
    async def wait_for_job_completion(self, run_id: int, poll_interval: int = 10) -> JobRun:
        """
        Wait for a job run to complete
        
        Args:
            run_id: Run ID to wait for
            poll_interval: Seconds between status checks
            
        Returns:
            Final JobRun object
        """
        self.logger.info(f"Waiting for job run {run_id} to complete...")
        
        while True:
            job_run = await self.get_job_run(run_id)
            
            if job_run.state in [JobState.TERMINATED, JobState.SKIPPED, JobState.INTERNAL_ERROR]:
                self.logger.info(f"Job run {run_id} completed with state: {job_run.state}")
                return job_run
            
            self.logger.info(f"Job run {run_id} is {job_run.state.value}, waiting...")
            await asyncio.sleep(poll_interval)
    
    async def run_jobs_parallel(self, job_configs: List[Dict[str, Any]], 
                               max_concurrent: int = 5,
                               poll_interval: int = 10) -> List[JobRun]:
        """
        Run multiple jobs in parallel and wait for completion
        
        Args:
            job_configs: List of job configurations with trigger parameters
            max_concurrent: Maximum number of concurrent jobs
            poll_interval: Seconds between status checks
            
        Returns:
            List of completed JobRun objects
        """
        self.logger.info(f"Starting parallel execution of {len(job_configs)} jobs")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_single_job(job_config: Dict[str, Any]) -> JobRun:
            async with semaphore:
                job_id = job_config["job_id"]
                trigger_params = job_config.get("trigger_params", {})
                
                # Trigger the job
                run_id = await self.trigger_job(job_id, **trigger_params)
                
                # Wait for completion
                return await self.wait_for_job_completion(run_id, poll_interval)
        
        # Execute all jobs concurrently
        tasks = [run_single_job(config) for config in job_configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        completed_jobs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Job {i} failed with exception: {result}")
            else:
                completed_jobs.append(result)
        
        self.logger.info(f"Completed {len(completed_jobs)} out of {len(job_configs)} jobs")
        return completed_jobs
    
    async def list_jobs(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all jobs in the workspace
        
        Args:
            limit: Maximum number of jobs to return
            offset: Offset for pagination
            
        Returns:
            List of job information dictionaries
        """
        try:
            response = await self._make_request("GET", f"list?limit={limit}&offset={offset}")
            return response.get("jobs", [])
        except Exception as e:
            self.logger.error(f"Failed to list jobs: {e}")
            raise
    
    async def delete_job(self, job_id: int) -> None:
        """
        Delete a job
        
        Args:
            job_id: ID of the job to delete
        """
        try:
            await self._make_request("POST", "delete", {"job_id": job_id})
            self.logger.info(f"Job {job_id} deleted successfully")
        except Exception as e:
            self.logger.error(f"Failed to delete job: {e}")
            raise
