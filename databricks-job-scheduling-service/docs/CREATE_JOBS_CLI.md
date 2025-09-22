# Create Jobs CLI Documentation

The `create_jobs.py` script provides a command-line interface for creating Databricks jobs from command line arguments or configuration files.

## Usage

```bash
# Using configuration file
python create_jobs.py --config-file CONFIG_FILE [OPTIONS]

# Using CLI arguments
python create_jobs.py --name JOB_NAME [CLUSTER_OPTIONS] [TASK_OPTIONS] [OTHER_OPTIONS]
```

## Arguments

### Configuration Source (Required - Choose One)

- `--config-file CONFIG_FILE`: JSON configuration file with job definitions
- `--name JOB_NAME`: Job name (required when not using config file)

### Cluster Configuration (Required for CLI mode - Choose One)

- `--new-cluster NEW_CLUSTER`: New cluster configuration as JSON string
- `--existing-cluster-id EXISTING_CLUSTER_ID`: Existing cluster ID
- `--compute COMPUTE`: Serverless compute configuration as JSON string

### Task Configuration (Required for CLI mode - Choose One)

- `--notebook-task NOTEBOOK_TASK`: Notebook task configuration as JSON string
- `--python-script-task PYTHON_SCRIPT_TASK`: Python script task configuration as JSON string
- `--spark-jar-task SPARK_JAR_TASK`: Spark JAR task configuration as JSON string
- `--spark-python-task SPARK_PYTHON_TASK`: Spark Python task configuration as JSON string
- `--spark-submit-task SPARK_SUBMIT_TASK`: Spark submit task configuration as JSON string

### Optional Configurations

- `--libraries LIBRARIES`: Libraries configuration as JSON string
- `--email-notifications EMAIL_NOTIFICATIONS`: Email notifications configuration as JSON string
- `--schedule SCHEDULE`: Schedule configuration as JSON string
- `--tags TAGS`: Tags configuration as JSON string

### Job Settings

- `--max-concurrent-runs MAX_CONCURRENT_RUNS`: Maximum concurrent runs (default: 1)
- `--timeout-seconds TIMEOUT_SECONDS`: Job timeout in seconds (default: 0 - no timeout)
- `--max-retries MAX_RETRIES`: Maximum number of retries (default: 0)
- `--retry-on-timeout`: Retry on timeout

### Output Options

- `--json-output`: Output results in JSON format
- `--quiet`: Suppress progress output, only show final results

## Examples

### Configuration File Examples

```bash
# Create single job from config file
python create_jobs.py --config-file examples/create_simple_notebook_job.json

# Create multiple jobs from config file
python create_jobs.py --config-file examples/create_multiple_jobs.json

# Create jobs with JSON output
python create_jobs.py --config-file examples/create_multiple_jobs.json --json-output --quiet
```

### CLI Argument Examples

```bash
# Create serverless notebook job
python create_jobs.py --name "my_notebook_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --compute '[{"compute_key": "default"}]'

# Create traditional cluster job
python create_jobs.py --name "cluster_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --new-cluster '{"spark_version": "15.4.x-scala2.12", "node_type_id": "i3.xlarge", "num_workers": 2}'

# Create job with libraries and tags
python create_jobs.py --name "complex_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --compute '[{"compute_key": "default"}]' --libraries '[{"pypi": {"package": "pandas"}}]' --tags '{"environment": "production"}'

# Create Python script job
python create_jobs.py --name "python_job" --python-script-task '{"python_file": "dbfs:/scripts/script.py"}' --compute '[{"compute_key": "default"}]'

# Create scheduled job
python create_jobs.py --name "scheduled_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --compute '[{"compute_key": "default"}]' --schedule '{"quartz_cron_expression": "0 0 2 * * ?", "timezone_id": "America/Los_Angeles"}'
```

## Configuration File Formats

### Single Job Configuration
```json
{
  "name": "simple_notebook_job",
  "compute": [
    {
      "compute_key": "default"
    }
  ],
  "notebook_task": {
    "notebook_path": "/Users/user@company.com/notebooks/simple_notebook"
  },
  "libraries": [
    {
      "pypi": {
        "package": "pandas"
      }
    }
  ],
  "timeout_seconds": 3600,
  "max_retries": 2,
  "retry_on_timeout": true,
  "tags": {
    "environment": "development",
    "team": "data-science"
  }
}
```

### Multiple Jobs Configuration
```json
[
  {
    "name": "data_processing_job",
    "compute": [
      {
        "compute_key": "default"
      }
    ],
    "notebook_task": {
      "notebook_path": "/Users/user@company.com/notebooks/data_processing",
      "base_parameters": {
        "input_path": "/data/input",
        "output_path": "/data/output"
      }
    },
    "libraries": [
      {
        "pypi": {
          "package": "pandas"
        }
      }
    ],
    "timeout_seconds": 7200,
    "max_retries": 3,
    "retry_on_timeout": true,
    "tags": {
      "environment": "production",
      "team": "data-engineering"
    }
  },
  {
    "name": "ml_training_job",
    "compute": [
      {
        "compute_key": "default"
      }
    ],
    "notebook_task": {
      "notebook_path": "/Users/user@company.com/notebooks/ml_training"
    },
    "libraries": [
      {
        "pypi": {
          "package": "scikit-learn"
        }
      }
    ],
    "timeout_seconds": 10800,
    "max_retries": 2,
    "retry_on_timeout": true,
    "email_notifications": {
      "on_start": ["ml-team@company.com"],
      "on_success": ["ml-team@company.com"],
      "on_failure": ["ml-team@company.com", "admin@company.com"]
    },
    "tags": {
      "environment": "production",
      "team": "ml-engineering"
    }
  }
]
```

### Traditional Cluster Job Configuration
```json
{
  "name": "traditional_cluster_job",
  "new_cluster": {
    "spark_version": "15.4.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 2,
    "spark_conf": {
      "spark.sql.adaptive.enabled": "true",
      "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
    },
    "aws_attributes": {
      "availability": "ON_DEMAND",
      "zone_id": "us-west-2a"
    },
    "driver_node_type_id": "i3.xlarge",
    "enable_elastic_disk": true
  },
  "notebook_task": {
    "notebook_path": "/Users/user@company.com/notebooks/traditional_notebook"
  },
  "libraries": [
    {
      "pypi": {
        "package": "pandas==2.0.3"
      }
    }
  ],
  "timeout_seconds": 7200,
  "max_retries": 3,
  "retry_on_timeout": true,
  "tags": {
    "environment": "production",
    "team": "data-engineering"
  }
}
```

### Scheduled Job Configuration
```json
{
  "name": "daily_etl_job",
  "compute": [
    {
      "compute_key": "default"
    }
  ],
  "notebook_task": {
    "notebook_path": "/Users/user@company.com/notebooks/daily_etl",
    "base_parameters": {
      "date": "${date}",
      "environment": "production"
    }
  },
  "libraries": [
    {
      "pypi": {
        "package": "pandas"
      }
    }
  ],
  "timeout_seconds": 14400,
  "max_retries": 2,
  "retry_on_timeout": true,
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "America/Los_Angeles",
    "pause_status": "UNPAUSED"
  },
  "email_notifications": {
    "on_start": ["etl-team@company.com"],
    "on_success": ["etl-team@company.com"],
    "on_failure": ["etl-team@company.com", "admin@company.com"]
  },
  "tags": {
    "environment": "production",
    "team": "data-engineering",
    "schedule": "daily"
  }
}
```

## Job Types

### Notebook Jobs
```bash
python create_jobs.py --name "notebook_job" --notebook-task '{"notebook_path": "/path/to/notebook", "base_parameters": {"param1": "value1"}}' --compute '[{"compute_key": "default"}]'
```

### Python Script Jobs
```bash
python create_jobs.py --name "python_job" --python-script-task '{"python_file": "dbfs:/scripts/script.py"}' --compute '[{"compute_key": "default"}]'
```

### Spark JAR Jobs
```bash
python create_jobs.py --name "jar_job" --spark-jar-task '{"jar_uri": "dbfs:/jars/app.jar", "main_class_name": "com.example.Main"}' --compute '[{"compute_key": "default"}]'
```

### Spark Python Jobs
```bash
python create_jobs.py --name "spark_python_job" --spark-python-task '{"python_file": "dbfs:/scripts/spark_script.py"}' --compute '[{"compute_key": "default"}]'
```

### Spark Submit Jobs
```bash
python create_jobs.py --name "spark_submit_job" --spark-submit-task '{"parameters": ["--class", "com.example.Main", "dbfs:/jars/app.jar"]}' --compute '[{"compute_key": "default"}]'
```

## Cluster Types

### Serverless Compute
```bash
python create_jobs.py --name "serverless_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --compute '[{"compute_key": "default"}]'
```

### Traditional Clusters
```bash
python create_jobs.py --name "cluster_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --new-cluster '{"spark_version": "15.4.x-scala2.12", "node_type_id": "i3.xlarge", "num_workers": 2}'
```

### Existing Clusters
```bash
python create_jobs.py --name "existing_cluster_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --existing-cluster-id "1234-567890-cluster123"
```

## Output Formats

### Standard Output
```
🔧 Databricks Job Creator
============================================================
Configuration file: examples/create_simple_notebook_job.json
============================================================
🚀 Creating 1 jobs...
============================================================
Creating job 1/1: simple_notebook_job
  ✅ Created job 'simple_notebook_job' with ID: 719952507413581

============================================================
📊 JOB CREATION RESULTS
============================================================

✅ Successfully created 1 jobs:
  • simple_notebook_job (ID: 719952507413581)

📈 SUMMARY
Total jobs: 1
Created: 1 ✅
Failed: 0 ❌
Success Rate: 100.0%

🎉 All jobs created successfully!
```

### JSON Output
```json
{
  "created_jobs": [
    {
      "name": "simple_notebook_job",
      "job_id": 719952507413581,
      "config": {
        "name": "simple_notebook_job",
        "compute": [{"compute_key": "default"}],
        "notebook_task": {
          "notebook_path": "/Users/user@company.com/notebooks/simple_notebook"
        },
        "libraries": [{"pypi": {"package": "pandas"}}],
        "timeout_seconds": 3600,
        "max_retries": 2,
        "retry_on_timeout": true,
        "tags": {
          "environment": "development",
          "team": "data-science"
        }
      }
    }
  ],
  "failed_jobs": [],
  "summary": {
    "total_jobs": 1,
    "success_count": 1,
    "failure_count": 0,
    "success_rate": 100.0
  }
}
```

## Exit Codes

- `0`: All jobs created successfully
- `1`: One or more jobs failed to create or an error occurred

## Error Handling

The script includes comprehensive error handling:

- **Configuration validation**: Invalid JSON or missing required fields are caught and reported
- **Job creation errors**: Failed job creation is tracked and reported
- **Network errors**: Connection issues are handled gracefully
- **File errors**: Missing or invalid configuration files are reported

## Best Practices

### Configuration File Management

#### File Organization
```bash
# Organize config files by environment and purpose
configs/
├── dev/
│   ├── simple_jobs.json
│   └── test_pipeline.json
├── staging/
│   ├── ml_training.json
│   └── data_processing.json
└── prod/
    ├── daily_etl.json
    ├── weekly_reports.json
    └── ml_inference.json
```

#### Version Control
- Store configuration files in version control
- Use descriptive names for different job sets
- Document parameter meanings in comments
- Keep sensitive data in environment variables

### For Production Use
```bash
# Use configuration files for complex job sets
python create_jobs.py --config-file prod/daily_etl.json --json-output --quiet

# Use environment-specific configs
python create_jobs.py --config-file configs/prod/ml_training.json

# Create jobs with proper tagging
python create_jobs.py --config-file prod/jobs.json --tags '{"environment": "production", "cost-center": "engineering"}'
```

### For Development/Testing
```bash
# Use simple config files for testing
python create_jobs.py --config-file dev/simple_jobs.json

# Create jobs with development tags
python create_jobs.py --name "test_job" --notebook-task '{"notebook_path": "/path/to/notebook"}' --compute '[{"compute_key": "default"}]' --tags '{"environment": "development"}'
```

### For Automation
```bash
# Use JSON output for integration with CI/CD
python create_jobs.py --config-file prod/jobs.json --json-output --quiet > job_creation_results.json

# Check creation results
if jq -e '.summary.failure_count > 0' job_creation_results.json; then
    echo "Some jobs failed to create!"
    exit 1
fi
```

## Integration Examples

### Bash Script Integration
```bash
#!/bin/bash
# Create jobs and check results
python create_jobs.py --config-file prod/jobs.json --json-output --quiet > results.json

# Check if all jobs were created successfully
if jq -e '.summary.failure_count > 0' results.json; then
    echo "Job creation failed!"
    jq '.failed_jobs[] | {name: .name, error: .error}' results.json
    exit 1
else
    echo "All jobs created successfully!"
    jq '.created_jobs[] | {name: .name, job_id: .job_id}' results.json
fi
```

### Python Integration
```python
import subprocess
import json

# Create jobs and get results
result = subprocess.run([
    'python', 'create_jobs.py', 
    '--config-file', 'prod/jobs.json',
    '--json-output', '--quiet'
], capture_output=True, text=True)

# Parse results
results = json.loads(result.stdout)
for job in results['created_jobs']:
    print(f"Created job '{job['name']}' with ID: {job['job_id']}")

if results['summary']['failure_count'] > 0:
    print("Some jobs failed to create!")
    for job in results['failed_jobs']:
        print(f"Failed: {job['name']} - {job['error']}")
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Create Databricks Jobs
  run: |
    python create_jobs.py --config-file ${{ env.JOB_CONFIG_FILE }} \
      --json-output --quiet > job_creation_results.json
    
    # Check results
    if jq -e '.summary.failure_count > 0' job_creation_results.json; then
      echo "Job creation failed!"
      cat job_creation_results.json
      exit 1
    fi
    
    # Store job IDs for later use
    jq -r '.created_jobs[] | "\(.name)=\(.job_id)"' job_creation_results.json >> $GITHUB_ENV
```

## Troubleshooting

### Common Issues

1. **"Invalid JSON in configuration file"**: Check JSON syntax in your config file
2. **"Each job configuration must have a 'name' field"**: Ensure all jobs have a name field
3. **"Must specify at least one task type"**: Provide a task configuration for CLI mode
4. **"Must specify cluster configuration"**: Provide cluster configuration for CLI mode
5. **"Job creation failed"**: Check Databricks permissions and job configuration

### Debug Mode
```bash
# Enable verbose logging
export DATABRICKS_LOG_LEVEL=DEBUG
python create_jobs.py --config-file examples/create_simple_notebook_job.json
```

## Environment Variables

The script uses the following environment variables (set via `.env` file or system environment):

- `DATABRICKS_HOST`: Databricks workspace URL
- `DATABRICKS_TOKEN`: Personal access token
- `DATABRICKS_TIMEOUT`: Request timeout (optional, default: 300)
