# Track Jobs CLI Documentation

The `track_jobs.py` script provides a command-line interface for triggering and tracking multiple Databricks jobs until completion with support for various job parameters.

## Usage

```bash
# Using job IDs directly
python track_jobs.py [OPTIONS] job_ids [job_ids ...]

# Using configuration file
python track_jobs.py [OPTIONS] --config-file CONFIG_FILE
```

## Arguments

### Positional Arguments

- `job_ids`: One or more job IDs to trigger and track (mutually exclusive with --config-file)

### Configuration File Option

- `--config-file CONFIG_FILE`: JSON configuration file with job definitions (mutually exclusive with job_ids)

### Optional Arguments

#### Job Parameters
- `--notebook-params NOTEBOOK_PARAMS`: Notebook parameters in format `'key1=value1,key2=value2'`
- `--python-params PYTHON_PARAMS`: Python parameters in format `'arg1,arg2,arg3'`
- `--jar-params JAR_PARAMS`: JAR parameters in format `'arg1,arg2,arg3'`
- `--python-named-params PYTHON_NAMED_PARAMS`: Python named parameters in format `'key1=value1,key2=value2'`

#### Execution Settings
- `--max-concurrent MAX_CONCURRENT`: Maximum number of concurrent jobs (default: 2)
- `--poll-interval POLL_INTERVAL`: Polling interval in seconds (default: 10)

#### Output Options
- `--json-output`: Output results in JSON format
- `--quiet`: Suppress progress output, only show final results

## Examples

### Basic Usage

```bash
# Track two jobs with default settings
python track_jobs.py 697909345169014 260482705947228

# Track a single job
python track_jobs.py 260482705947228
```

### With Job Parameters

```bash
# Track job with notebook parameters
python track_jobs.py 260482705947228 --notebook-params "input_path=/path/to/input,output_path=/path/to/output,model_version=v1.0"

# Track job with Python parameters
python track_jobs.py 260482705947228 --python-params "arg1,arg2,arg3"

# Track job with JAR parameters
python track_jobs.py 260482705947228 --jar-params "input,output,config.json"

# Track job with Python named parameters
python track_jobs.py 260482705947228 --python-named-params "input_path=/data/input,output_path=/data/output"
```

### With Execution Settings

```bash
# Track jobs with custom concurrency and polling
python track_jobs.py 697909345169014 260482705947228 --max-concurrent 3 --poll-interval 15

# Track jobs with single concurrency (sequential execution)
python track_jobs.py 697909345169014 260482705947228 --max-concurrent 1
```

### Output Options

```bash
# Get JSON output for programmatic use
python track_jobs.py 260482705947228 --json-output

# Quiet mode with JSON output (minimal logging)
python track_jobs.py 260482705947228 --json-output --quiet

# Quiet mode with regular output
python track_jobs.py 260482705947228 --quiet
```

### Configuration File Examples

```bash
# Track jobs from configuration file
python track_jobs.py --config-file job_configs.json

# Track jobs from config file with custom settings
python track_jobs.py --config-file job_configs.json --max-concurrent 4 --poll-interval 5

# Override parameters from config file
python track_jobs.py --config-file job_configs.json --notebook-params "override_param=value"

# JSON output with config file
python track_jobs.py --config-file job_configs.json --json-output --quiet
```

### Complex Examples

```bash
# Track multiple jobs with different parameter types
python track_jobs.py 697909345169014 260482705947228 --notebook-params "param1=value1" --python-params "arg1,arg2"

# Track jobs with custom settings and JSON output
python track_jobs.py 697909345169014 260482705947228 --max-concurrent 4 --poll-interval 5 --json-output --quiet
```

## Configuration File Formats

### Single Job Configuration
```json
{
  "job_id": 260482705947228,
  "trigger_params": {}
}
```

### Multiple Jobs Configuration
```json
[
  {
    "job_id": 697909345169014,
    "trigger_params": {
      "notebook_params": {
        "input_path": "/path/to/input1",
        "output_path": "/path/to/output1",
        "model_version": "v1.0"
      }
    }
  },
  {
    "job_id": 260482705947228,
    "trigger_params": {
      "python_params": [
        "--input-path", "/path/to/input2",
        "--output-path", "/path/to/output2"
      ]
    }
  }
]
```

### Mixed Job Types Configuration
```json
[
  {
    "job_id": 260482705947228,
    "trigger_params": {
      "notebook_params": {
        "input_path": "/data/input",
        "output_path": "/data/output"
      }
    }
  },
  {
    "job_id": 697909345169014,
    "trigger_params": {
      "python_params": ["arg1", "arg2", "arg3"],
      "python_named_params": {
        "model_type": "random_forest",
        "max_depth": "10"
      }
    }
  }
]
```

## Parameter Formats

### Notebook Parameters
Format: `key1=value1,key2=value2,key3=value3`

Example:
```bash
--notebook-params "input_path=/data/input,output_path=/data/output,model_version=v2.0"
```

### Python Parameters
Format: `arg1,arg2,arg3`

Example:
```bash
--python-params "arg1,arg2,arg3"
```

### JAR Parameters
Format: `arg1,arg2,arg3`

Example:
```bash
--jar-params "input,output,config.json"
```

### Python Named Parameters
Format: `key1=value1,key2=value2,key3=value3`

Example:
```bash
--python-named-params "input_path=/data/input,output_path=/data/output"
```

## Output Formats

### Standard Output
```
🔧 Databricks Job Tracker
============================================================
Tracking jobs: [260482705947228]
With parameters:
  Notebook: input_path=/test/input,output_path=/test/output
============================================================
🚀 Starting to track 1 jobs: [260482705947228]
============================================================
⚡ Triggering 1 jobs in parallel...
...
============================================================
📊 JOB EXECUTION RESULTS
============================================================

🔍 Job 1 (ID: 260482705947228)
   Run ID: 199838941833231
   Final State: TERMINATED
   Result State: SUCCESS
   Start Time: 2025-09-21T23:18:35.436000
   End Time: 2025-09-21T23:18:55.414000
   Duration: 19.98 seconds
   Run Page: https://dbc-1d105d44-a856.cloud.databricks.com/...

   ✅ SUCCESS

============================================================
📈 SUMMARY
============================================================
Total Jobs: 1
Successful: 1 ✅
Failed: 0 ❌
Success Rate: 100.0%

🎉 All jobs completed successfully!
```

### JSON Output
```json
[
  {
    "job_id": 260482705947228,
    "run_id": 199838941833231,
    "state": "TERMINATED",
    "result_state": "SUCCESS",
    "start_time": "2025-09-21T23:18:35.436000",
    "end_time": "2025-09-21T23:18:55.414000",
    "duration_seconds": 19.978,
    "error_message": "",
    "run_page_url": "https://dbc-1d105d44-a856.cloud.databricks.com/...",
    "success": true
  }
]
```

## Exit Codes

- `0`: All jobs completed successfully
- `1`: One or more jobs failed or an error occurred

## Error Handling

The script includes comprehensive error handling:

- **Parameter validation**: Invalid parameter formats are caught and reported
- **Job execution errors**: Failed jobs are tracked and reported
- **Network errors**: Connection issues are handled gracefully
- **Timeout handling**: Long-running jobs are handled with configurable timeouts

## Best Practices

### Configuration File Management

#### File Organization
```bash
# Organize config files by environment
configs/
├── dev/
│   ├── simple_jobs.json
│   └── complex_pipeline.json
├── staging/
│   ├── ml_training.json
│   └── data_processing.json
└── prod/
    ├── daily_etl.json
    └── weekly_reports.json
```

#### Version Control
- Store configuration files in version control
- Use descriptive names for different job sets
- Document parameter meanings in comments
- Keep sensitive data in environment variables

#### Parameter Management
```json
{
  "job_id": 260482705947228,
  "trigger_params": {
    "notebook_params": {
      "input_path": "${INPUT_PATH}",
      "output_path": "${OUTPUT_PATH}",
      "model_version": "${MODEL_VERSION}"
    }
  }
}
```

### For Production Use
```bash
# Use configuration files for complex job sets
python track_jobs.py --config-file prod/daily_etl.json --json-output --quiet

# Use environment-specific configs
python track_jobs.py --config-file configs/prod/ml_training.json --max-concurrent 3

# Override specific parameters for different runs
python track_jobs.py --config-file prod/daily_etl.json --notebook-params "date=${TODAY}"
```

### For Development/Testing
```bash
# Use simple config files for testing
python track_jobs.py --config-file dev/simple_jobs.json --poll-interval 5

# Use single concurrency for debugging
python track_jobs.py --config-file dev/test_jobs.json --max-concurrent 1
```

### For Monitoring
```bash
# Use JSON output for integration with monitoring systems
python track_jobs.py --config-file prod/daily_etl.json --json-output --quiet | jq '.[] | select(.success == false)'

# Monitor specific job types
python track_jobs.py --config-file prod/ml_training.json --json-output --quiet | jq '.[] | {job_id, success, duration_seconds}'
```

## Integration Examples

### Bash Script Integration
```bash
#!/bin/bash
# Run jobs and check results
python track_jobs.py 697909345169014 260482705947228 --json-output --quiet > results.json

# Check if all jobs succeeded
if jq -e '.[] | select(.success == false)' results.json > /dev/null; then
    echo "Some jobs failed!"
    exit 1
else
    echo "All jobs succeeded!"
    exit 0
fi
```

### Python Integration
```python
import subprocess
import json

# Run track_jobs and get results
result = subprocess.run([
    'python', 'track_jobs.py', '260482705947228',
    '--json-output', '--quiet'
], capture_output=True, text=True)

# Parse results
results = json.loads(result.stdout)
for job in results:
    print(f"Job {job['job_id']}: {job['result_state']}")
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Run Databricks Jobs
  run: |
    python track_jobs.py ${{ env.JOB_ID_1 }} ${{ env.JOB_ID_2 }} \
      --notebook-params "input_path=${{ env.INPUT_PATH }},output_path=${{ env.OUTPUT_PATH }}" \
      --json-output --quiet > job_results.json
    
    # Check results
    if jq -e '.[] | select(.success == false)' job_results.json; then
      echo "Job execution failed!"
      exit 1
    fi
```

## Troubleshooting

### Common Issues

1. **"Invalid parameter format"**: Check parameter syntax (use `key=value` for named params, `arg1,arg2` for positional params)

2. **"Job not found"**: Verify job IDs are correct and accessible

3. **"Authentication failed"**: Check `DATABRICKS_HOST` and `DATABRICKS_TOKEN` environment variables

4. **"Timeout errors"**: Increase `--poll-interval` or check job complexity

### Debug Mode
```bash
# Enable verbose logging
export DATABRICKS_LOG_LEVEL=DEBUG
python track_jobs.py 260482705947228
```

## Environment Variables

The script uses the following environment variables (set via `.env` file or system environment):

- `DATABRICKS_HOST`: Databricks workspace URL
- `DATABRICKS_TOKEN`: Personal access token
- `DATABRICKS_TIMEOUT`: Request timeout (optional, default: 300)
- `DATABRICKS_MAX_CONCURRENT_JOBS`: Default max concurrent jobs (optional, default: 5)
- `DATABRICKS_POLL_INTERVAL`: Default poll interval (optional, default: 10)
