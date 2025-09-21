# Databricks Cluster Types Support

This document explains the different cluster types supported by the Databricks Job Scheduling Service and provides examples for each.

## Cluster Types Overview

The Databricks Job Scheduling Service supports two main cluster types:

1. **Serverless Compute** - Fully managed compute with automatic scaling
2. **Traditional Clusters** - User-managed clusters with full control over configuration

## Serverless Compute

### When to Use
- **Fully managed compute** - No cluster management required
- **Automatic scaling** - Scales up and down based on workload
- **Cost-effective** - Pay only for compute time used
- **Simplified configuration** - Minimal setup required

### Configuration
```python
job_config = JobConfig(
    name="serverless_job",
    compute=[{"compute_key": "default"}],
    notebook_task={
        "notebook_path": "/path/to/notebook"
    },
    libraries=[
        {"pypi": {"package": "pandas"}},
        {"pypi": {"package": "scikit-learn"}}
    ]
)
```

### Key Features
- ✅ Automatic scaling
- ✅ No cluster management
- ✅ Pay-per-use pricing
- ✅ Libraries in environment spec
- ❌ No custom Spark configuration
- ❌ No cluster customization

### Example Files
- `examples/notebook_job_config.json`
- `examples/python_script_job_config.json`

## Traditional Clusters

### When to Use
- **Full control** over cluster configuration
- **Custom Spark settings** required
- **Specific instance types** needed
- **Cost optimization** with spot instances
- **Custom initialization scripts**

### Configuration
```python
job_config = JobConfig(
    name="traditional_job",
    new_cluster={
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
        "enable_elastic_disk": True
    },
    notebook_task={
        "notebook_path": "/path/to/notebook"
    },
    libraries=[
        {"pypi": {"package": "pandas"}},
        {"pypi": {"package": "scikit-learn"}}
    ]
)
```

### Key Features
- ✅ Full cluster customization
- ✅ Custom Spark configuration
- ✅ Spot instance support
- ✅ Custom initialization scripts
- ✅ Multiple instance types
- ✅ Cost optimization options
- ❌ Manual cluster management
- ❌ Higher complexity

### Example Files
- `examples/traditional_cluster_notebook_job.json`
- `examples/traditional_cluster_python_job.json`
- `examples/traditional_cluster_spark_jar_job.json`
- `examples/traditional_cluster_existing_cluster_job.json`

## Cluster Configuration Options

### Traditional Cluster Settings

#### Basic Configuration
```python
new_cluster = {
    "spark_version": "15.4.x-scala2.12",  # Spark version
    "node_type_id": "i3.xlarge",          # Instance type
    "num_workers": 2,                     # Number of workers
    "driver_node_type_id": "i3.xlarge"    # Driver node type (optional)
}
```

#### AWS-Specific Configuration
```python
aws_attributes = {
    "availability": "ON_DEMAND",          # or "SPOT"
    "zone_id": "us-west-2a",             # Availability zone
    "spot_bid_price_percent": 100,       # Spot bid price (for spot instances)
    "first_on_demand": 1                 # On-demand instances before spot
}
```

#### Spark Configuration
```python
spark_conf = {
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    "spark.sql.adaptive.skewJoin.enabled": "true"
}
```

#### Additional Features
```python
cluster_config = {
    "enable_elastic_disk": True,          # Auto-scaling disk
    "init_scripts": [                     # Initialization scripts
        {
            "dbfs": {
                "destination": "dbfs:/init-scripts/setup.sh"
            }
        }
    ],
    "custom_tags": {                      # Custom tags
        "Environment": "production",
        "Owner": "data-team"
    }
}
```

### Serverless Compute Settings

```python
compute = [
    {
        "compute_key": "default"          # Compute key (usually "default")
    }
]
```

## Job Types by Cluster Type

### Notebook Jobs

#### Serverless
```python
notebook_task = {
    "notebook_path": "/path/to/notebook",
    "base_parameters": {"param1": "value1"}
}
```

#### Traditional
```python
notebook_task = {
    "notebook_path": "/path/to/notebook",
    "base_parameters": {"param1": "value1"}
}
```

### Python Script Jobs

#### Serverless
```python
python_script_task = {
    "python_file": "dbfs:/path/to/script.py"
}
```

#### Traditional
```python
python_script_task = {
    "python_file": "dbfs:/path/to/script.py"
}
```

### Spark JAR Jobs

#### Serverless
```python
spark_jar_task = {
    "jar_uri": "dbfs:/path/to/jar.jar",
    "main_class_name": "com.example.MainClass"
}
```

#### Traditional
```python
spark_jar_task = {
    "jar_uri": "dbfs:/path/to/jar.jar",
    "main_class_name": "com.example.MainClass"
}
```

## Library Configuration

### Serverless Compute
Libraries are placed in the environment spec:
```python
# In the task configuration
task["environment"] = {
    "spec": {
        "libraries": [
            {"pypi": {"package": "pandas"}},
            {"pypi": {"package": "scikit-learn"}}
        ]
    }
}
```

### Traditional Clusters
Libraries are placed directly in the task:
```python
task["libraries"] = [
    {"pypi": {"package": "pandas"}},
    {"pypi": {"package": "scikit-learn"}},
    {"jar": "dbfs:/libraries/custom.jar"},
    {"maven": {"coordinates": "org.apache.spark:spark-sql_2.12:3.4.0"}}
]
```

## Cost Optimization

### Serverless Compute
- **Pay-per-use**: Only pay for actual compute time
- **Automatic scaling**: No idle time costs
- **No management overhead**: No cluster management costs

### Traditional Clusters
- **Spot instances**: Up to 90% cost savings
- **Right-sizing**: Choose appropriate instance types
- **Scheduled jobs**: Use existing clusters for cost efficiency
- **Auto-termination**: Configure cluster auto-termination

## Choosing the Right Cluster Type

### Choose Serverless When:
- ✅ You want fully managed compute
- ✅ Workloads are variable or unpredictable
- ✅ You want to minimize management overhead
- ✅ You're okay with limited customization
- ✅ Cost predictability is important

### Choose Traditional When:
- ✅ You need specific Spark configurations
- ✅ You want to use spot instances for cost savings
- ✅ You have predictable workloads
- ✅ You need custom initialization scripts
- ✅ You want full control over cluster configuration

## Workspace Compatibility

### Serverless-Only Workspaces
- Some Databricks workspaces only support serverless compute
- Traditional cluster configurations will fail with "Only serverless compute is supported"
- Use `compute` configuration instead of `new_cluster`

### Traditional Cluster Workspaces
- Support both serverless and traditional clusters
- Can use either configuration type
- Choose based on your specific requirements

## Migration Between Cluster Types

### From Serverless to Traditional
1. Replace `compute` with `new_cluster` configuration
2. Move libraries from `environment.spec.libraries` to `libraries`
3. Add any required Spark configuration
4. Test thoroughly in your environment

### From Traditional to Serverless
1. Replace `new_cluster` with `compute` configuration
2. Move libraries to `environment.spec.libraries`
3. Remove cluster-specific configurations
4. Test thoroughly in your environment

## Best Practices

### Serverless Compute
- Use for development and testing
- Ideal for variable workloads
- Keep libraries minimal
- Use for quick prototyping

### Traditional Clusters
- Use for production workloads
- Optimize for cost with spot instances
- Configure appropriate timeouts
- Use existing clusters when possible
- Monitor cluster utilization

## Troubleshooting

### Common Issues

#### "Only serverless compute is supported"
- Your workspace only supports serverless compute
- Use `compute` configuration instead of `new_cluster`

#### "Libraries field is not supported for serverless task"
- Move libraries to `environment.spec.libraries` for serverless compute

#### Cluster startup failures
- Check instance type availability in your region
- Verify AWS permissions for cluster creation
- Check spot instance availability

#### Job timeout issues
- Increase `timeout_seconds` for long-running jobs
- Optimize your code for better performance
- Consider using larger instance types
