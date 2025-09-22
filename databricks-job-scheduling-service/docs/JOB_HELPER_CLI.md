# Job Helper CLI Documentation

The `job_helper.py` script provides a comprehensive helper for listing Databricks jobs, filtering by name, and generating track_jobs configurations. It integrates with the [Databricks Jobs List API](https://docs.databricks.com/api/workspace/jobs/list) to provide powerful job management capabilities.

## Features

- **List Jobs**: View all jobs with optional name filtering and detailed information
- **Interactive Selection**: Select multiple jobs through an interactive interface
- **Config Generation**: Generate track_jobs configuration files from selected jobs
- **Parameter Extraction**: Automatically detect and include existing job parameters
- **Name Filtering**: Filter jobs by name using case-insensitive partial matching
- **Pagination Support**: Handle large numbers of jobs with limit and offset parameters
- **JSON Output**: Support for both human-readable and JSON output formats
- **Parameter Merging**: Combine existing job parameters with default parameters

## Usage

```bash
python job_helper.py {list,select,config} [OPTIONS]
```

## Commands

### 1. List Jobs (`list`)

List Databricks jobs with optional filtering and detailed information.

```bash
python job_helper.py list [OPTIONS]
```

**Options:**
- `--name-filter TEXT`: Filter jobs by name (case-insensitive partial match)
- `--details`: Show detailed job information including task type, cluster info, and tags
- `--limit INT`: Maximum number of jobs to return (default: 100)
- `--offset INT`: Offset for pagination (default: 0)
- `--json-output`: Output in JSON format

**Examples:**
```bash
# List all jobs
python job_helper.py list

# List jobs with name filter
python job_helper.py list --name-filter "etl"

# List jobs with detailed information
python job_helper.py list --name-filter "ml" --details

# List jobs with pagination
python job_helper.py list --limit 10 --offset 20

# JSON output for automation
python job_helper.py list --name-filter "data" --json-output
```

### 2. Interactive Selection (`select`)

Interactive job selection and configuration generation.

```bash
python job_helper.py select [OPTIONS]
```

**Options:**
- `--name-filter TEXT`: Filter jobs by name (case-insensitive partial match)
- `--details`: Show detailed job information
- `--limit INT`: Maximum number of jobs to return (default: 100)
- `--output-file PATH`: Output file for generated configuration
- `--default-params JSON`: Default trigger parameters as JSON string
- `--no-existing-params`: Do not include existing job parameters

**Examples:**
```bash
# Interactive selection with name filter
python job_helper.py select --name-filter "data"

# Interactive selection with details
python job_helper.py select --name-filter "ml" --details

# Generate config with existing parameters preserved
python job_helper.py select --name-filter "etl"

# Override existing parameters with defaults
python job_helper.py select --name-filter "etl" --default-params '{"notebook_params": {"env": "prod"}}'

# Ignore existing parameters, use only defaults
python job_helper.py select --name-filter "etl" --no-existing-params --default-params '{"notebook_params": {"env": "prod"}}'

# Save configuration to file
python job_helper.py select --name-filter "training" --output-file my_jobs_config.json
```

### 3. Generate Configuration (`config`)

Generate track_jobs configuration for specific job IDs.

```bash
python job_helper.py config --job-ids JOB_IDS [OPTIONS]
```

**Options:**
- `--job-ids TEXT`: Comma-separated job IDs (required)
- `--output-file PATH`: Output file for generated configuration
- `--default-params JSON`: Default trigger parameters as JSON string
- `--no-existing-params`: Do not include existing job parameters
- `--json-output`: Output in JSON format

**Examples:**
```bash
# Generate config for specific jobs
python job_helper.py config --job-ids 123,456,789

# Generate config with existing parameters preserved
python job_helper.py config --job-ids 123,456

# Override existing parameters with defaults
python job_helper.py config --job-ids 123,456 --default-params '{"notebook_params": {"env": "prod"}}'

# Ignore existing parameters, use only defaults
python job_helper.py config --job-ids 123,456 --no-existing-params --default-params '{"notebook_params": {"env": "prod"}}'

# Save configuration to file
python job_helper.py config --job-ids 123,456 --output-file my_config.json

# JSON output
python job_helper.py config --job-ids 123 --json-output
```

## Output Formats

### Standard List Output
```
Found 3 jobs:
================================================================================
ID: 875836500482239 | Name: ml_training_job | Created: 2025-09-21 23:40:12 | Creator: user@company.com
ID: 939660446892057 | Name: data_processing_job | Created: 2025-09-21 23:40:11 | Creator: user@company.com
ID: 719952507413581 | Name: simple_notebook_job | Created: 2025-09-21 23:39:41 | Creator: user@company.com
```

### Detailed List Output
```
Found 1 jobs:
================================================================================
ID: 875836500482239 | Name: ml_training_job | Created: 2025-09-21 23:40:12 | Creator: user@company.com
  Type: Notebook | Cluster: Serverless Compute | Timeout: 10800s | Retries: 0 | Max Concurrent: 1
  Tags: environment=production, team=ml-engineering, workload=training
```

### Interactive Selection
```
Found 2 jobs:
================================================================================
 1. ID: 694312283520679 | Name: simple_notebook_job | Created: 2025-09-21 23:40:39 | Creator: user@company.com
 2. ID: 719952507413581 | Name: simple_notebook_job | Created: 2025-09-21 23:39:41 | Creator: user@company.com

Select jobs to track (comma-separated numbers, e.g., 1,3,5 or 'all' for all jobs):
Selection: 1,2

Generated track_jobs configuration:
==================================================
[
  {
    "job_id": 694312283520679,
    "trigger_params": {}
  },
  {
    "job_id": 719952507413581,
    "trigger_params": {}
  }
]

To use this configuration:
python track_jobs.py --config-file generated_config.json
```

### JSON Output
```json
[
  {
    "job_id": 875836500482239,
    "creator_user_name": "user@company.com",
    "run_as_user_name": "user@company.com",
    "settings": {
      "name": "ml_training_job",
      "email_notifications": {
        "on_start": ["ml-team@company.com"],
        "on_success": ["ml-team@company.com"],
        "on_failure": ["ml-team@company.com", "admin@company.com"]
      },
      "timeout_seconds": 10800,
      "max_concurrent_runs": 1,
      "tags": {
        "environment": "production",
        "team": "ml-engineering",
        "workload": "training"
      },
      "format": "MULTI_TASK"
    },
    "created_time": 1758512412369
  }
]
```

## Parameter Extraction

The job helper automatically detects and extracts existing job parameters from job configurations. This ensures that generated track_jobs configurations preserve the job's current parameter structure.

### Supported Parameter Types

- **Job Parameters**: `parameters` from job-level settings (apply to all tasks)
- **Notebook Parameters**: `base_parameters` from notebook tasks
- **Python Parameters**: `parameters` from Python script tasks  
- **Spark Python Parameters**: `parameters` from Spark Python tasks
- **JAR Parameters**: `parameters` from Spark JAR tasks
- **Spark Submit Parameters**: `parameters` from Spark submit tasks

### Parameter Merging Logic

1. **Start with existing parameters**: Extract current job parameters
2. **Apply default parameters**: Override with provided default parameters
3. **Merge task parameters**: When both job_parameters and notebook_params exist, merge them together
4. **Preserve job structure**: Maintain the original parameter format

#### Merging Behavior:
- **job_parameters + notebook_params**: notebook_params are merged into job_parameters
- **Overlapping parameters**: notebook_params override job_parameters with the same key
- **New parameters**: notebook_params not in job_parameters are added
- **Legacy parameters**: python_params, jar_params, python_named_params are ignored when job_parameters exist

### Examples

#### Job with Existing Parameters
```bash
# Job has: job_parameters = [{"name": "param_1", "default": "value1"}]
#         notebook_params = {"model_type": "random_forest", "test_size": "0.2"}
python job_helper.py config --job-ids 123

# Generated config:
{
  "job_id": 123,
  "trigger_params": {
    "job_parameters": [
      {
        "name": "param_1",
        "default": "value1"
      }
    ],
    "notebook_params": {
      "model_type": "random_forest",
      "test_size": "0.2"
    }
  }
}
```

#### Override Existing Parameters
```bash
# Override with default parameters
python job_helper.py config --job-ids 123 --default-params '{"notebook_params": {"model_type": "xgboost", "test_size": "0.3"}}'

# Generated config:
{
  "job_id": 123,
  "trigger_params": {
    "job_parameters": [
      {
        "name": "param_1",
        "default": "value1"
      }
    ],
    "notebook_params": {
      "model_type": "xgboost",  # Overridden
      "test_size": "0.3"        # Overridden
    }
  }
}
```

#### Merge Parameters
```bash
# Job has: job_parameters = [{"name": "param_1", "default": "value1"}]
#         notebook_params = {"model_type": "random_forest", "test_size": "0.2"}
python job_helper.py config --job-ids 123

# Generated config (merged):
{
  "job_id": 123,
  "trigger_params": {
    "job_parameters": [
      {
        "name": "param_1",
        "default": "value1"
      }
    ],
    "notebook_params": {
      "model_type": "random_forest",
      "test_size": "0.2"
    }
  }
}

# When triggered, parameters are merged:
# Final job_parameters: [
#   {"key": "param_1", "value": "value1"},
#   {"key": "model_type", "value": "random_forest"},
#   {"key": "test_size", "value": "0.2"}
# ]
```

#### Skip Existing Parameters
```bash
# Ignore existing parameters, use only defaults
python job_helper.py config --job-ids 123 --no-existing-params --default-params '{"notebook_params": {"env": "prod"}}'

# Generated config:
{
  "job_id": 123,
  "trigger_params": {
    "notebook_params": {
      "env": "prod"
    }
  }
}
```

## Generated Configuration Formats

### Single Job Configuration
```json
{
  "job_id": 875836500482239,
  "trigger_params": {
    "notebook_params": {
      "env": "production",
      "model_version": "v2.0"
    }
  }
}
```

### Multiple Jobs Configuration
```json
[
  {
    "job_id": 875836500482239,
    "trigger_params": {
      "notebook_params": {
        "env": "production",
        "model_version": "v2.0"
      }
    }
  },
  {
    "job_id": 939660446892057,
    "trigger_params": {
      "python_params": ["--env", "production"],
      "python_named_params": {
        "batch_size": "32"
      }
    }
  }
]
```

## Use Cases

### 1. Job Discovery and Management

```bash
# Find all ETL jobs
python job_helper.py list --name-filter "etl" --details

# Find jobs created by specific user
python job_helper.py list --json-output | jq '.[] | select(.creator_user_name == "user@company.com")'

# Find jobs with specific tags
python job_helper.py list --json-output | jq '.[] | select(.settings.tags.environment == "production")'
```

### 2. Batch Job Configuration

```bash
# Generate config for all ML jobs
python job_helper.py select --name-filter "ml" --default-params '{"notebook_params": {"env": "prod"}}' --output-file ml_jobs.json

# Generate config for specific job IDs
python job_helper.py config --job-ids 123,456,789 --default-params '{"notebook_params": {"env": "staging"}}' --output-file staging_jobs.json
```

### 3. Automation and CI/CD

```bash
# List jobs and generate config in one command
python job_helper.py select --name-filter "daily" --output-file daily_jobs.json --default-params '{"notebook_params": {"date": "${date}"}}'

# Use in CI/CD pipeline
python job_helper.py config --job-ids $JOB_IDS --output-file job_config.json
python track_jobs.py --config-file job_config.json
```

### 4. Job Monitoring and Analysis

```bash
# Get all jobs with details for analysis
python job_helper.py list --details --json-output > all_jobs.json

# Find jobs by creation time
python job_helper.py list --json-output | jq '.[] | select(.created_time > 1758512400000)'

# Find jobs by timeout
python job_helper.py list --json-output | jq '.[] | select(.settings.timeout_seconds > 3600)'
```

## Integration Examples

### Bash Script Integration
```bash
#!/bin/bash
# Find and track all ETL jobs
python job_helper.py select --name-filter "etl" --output-file etl_jobs.json --default-params '{"notebook_params": {"env": "production"}}'

if [ -f etl_jobs.json ]; then
    echo "Tracking ETL jobs..."
    python track_jobs.py --config-file etl_jobs.json
else
    echo "No ETL jobs found"
fi
```

### Python Integration
```python
import subprocess
import json

# Get jobs and generate config
result = subprocess.run([
    'python', 'job_helper.py', 'list', 
    '--name-filter', 'ml', 
    '--json-output'
], capture_output=True, text=True)

jobs = json.loads(result.stdout)
job_ids = [str(job['job_id']) for job in jobs]

# Generate config
config_result = subprocess.run([
    'python', 'job_helper.py', 'config',
    '--job-ids', ','.join(job_ids),
    '--default-params', '{"notebook_params": {"env": "prod"}}',
    '--output-file', 'ml_jobs.json'
])

# Track jobs
subprocess.run(['python', 'track_jobs.py', '--config-file', 'ml_jobs.json'])
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Find and Track Jobs
  run: |
    # Find jobs by name pattern
    python job_helper.py select --name-filter "${{ env.JOB_PATTERN }}" \
      --output-file jobs.json \
      --default-params '{"notebook_params": {"env": "${{ env.ENVIRONMENT }}"}}'
    
    # Track jobs if any found
    if [ -f jobs.json ]; then
      python track_jobs.py --config-file jobs.json
    fi
```

## Advanced Usage

### Custom Filtering with jq
```bash
# Find jobs by multiple criteria
python job_helper.py list --json-output | jq '.[] | select(.settings.tags.team == "data-engineering" and .settings.timeout_seconds > 3600)'

# Find jobs created in last 24 hours
python job_helper.py list --json-output | jq '.[] | select(.created_time > (now - 86400) * 1000)'

# Find jobs with specific email notifications
python job_helper.py list --json-output | jq '.[] | select(.settings.email_notifications.on_failure | length > 1)'
```

### Batch Operations
```bash
# Generate configs for different job categories
python job_helper.py select --name-filter "etl" --output-file etl_jobs.json
python job_helper.py select --name-filter "ml" --output-file ml_jobs.json
python job_helper.py select --name-filter "report" --output-file report_jobs.json

# Track all job categories
for config in etl_jobs.json ml_jobs.json report_jobs.json; do
    if [ -f "$config" ]; then
        echo "Tracking jobs from $config"
        python track_jobs.py --config-file "$config"
    fi
done
```

### Environment-Specific Configurations
```bash
# Development environment
python job_helper.py select --name-filter "dev" --default-params '{"notebook_params": {"env": "dev", "debug": "true"}}' --output-file dev_jobs.json

# Production environment
python job_helper.py select --name-filter "prod" --default-params '{"notebook_params": {"env": "prod", "debug": "false"}}' --output-file prod_jobs.json

# Staging environment
python job_helper.py select --name-filter "staging" --default-params '{"notebook_params": {"env": "staging", "debug": "true"}}' --output-file staging_jobs.json
```

## Error Handling

The script includes comprehensive error handling:

- **API Errors**: Network issues and API errors are caught and reported
- **Invalid Input**: Malformed job IDs or JSON parameters are validated
- **File Errors**: Missing or invalid configuration files are handled
- **Selection Errors**: Invalid job selections are caught and re-prompted

## Environment Variables

The script uses the following environment variables (set via `.env` file or system environment):

- `DATABRICKS_HOST`: Databricks workspace URL
- `DATABRICKS_TOKEN`: Personal access token
- `DATABRICKS_TIMEOUT`: Request timeout (optional, default: 300)

## Best Practices

### 1. Use Name Filtering
```bash
# Always use name filters to narrow down results
python job_helper.py list --name-filter "etl" --details
```

### 2. Save Configurations
```bash
# Always save generated configurations for reuse
python job_helper.py select --name-filter "ml" --output-file ml_jobs.json
```

### 3. Use Default Parameters
```bash
# Set appropriate default parameters for your environment
python job_helper.py config --job-ids 123,456 --default-params '{"notebook_params": {"env": "production"}}'
```

### 4. Combine with track_jobs
```bash
# Generate config and immediately track jobs
python job_helper.py select --name-filter "daily" --output-file daily_jobs.json
python track_jobs.py --config-file daily_jobs.json
```

### 5. Use JSON Output for Automation
```bash
# Use JSON output for programmatic processing
python job_helper.py list --name-filter "ml" --json-output | jq '.[] | .job_id'
```

## Troubleshooting

### Common Issues

1. **"No jobs found matching the criteria"**: Check your name filter or try without filter
2. **"Invalid job IDs"**: Ensure job IDs exist and are correctly formatted
3. **"Error parsing default parameters"**: Check JSON syntax in default parameters
4. **"HTTP request failed"**: Check Databricks credentials and network connectivity

### Debug Mode
```bash
# Enable verbose logging
export DATABRICKS_LOG_LEVEL=DEBUG
python job_helper.py list --name-filter "test"
```

### Validation
```bash
# Validate generated configuration
python job_helper.py config --job-ids 123 --json-output | jq .

# Test configuration with track_jobs
python job_helper.py select --name-filter "test" --output-file test.json
python track_jobs.py --config-file test.json --dry-run
```

This job helper provides a powerful interface for managing Databricks jobs and generating configurations for the track_jobs script, making it easy to discover, select, and track jobs programmatically.
