#!/usr/bin/env python3
"""
Simple Ray test script to verify cluster functionality
"""

import ray
import time
import random

def main():
    print("🚀 Starting Ray test...")
    
    # Initialize Ray
    ray.init(address="auto")
    print("✅ Connected to Ray cluster")
    
    @ray.remote
    def process_data(data):
        """Process some data with a random delay"""
        time.sleep(random.uniform(0.1, 0.5))
        return data * 2
    
    @ray.remote
    def aggregate_results(results):
        """Aggregate results from multiple tasks"""
        return sum(results)
    
    # Create some sample data
    data = list(range(1, 21))  # [1, 2, 3, ..., 20]
    print(f"📊 Processing {len(data)} data points")
    
    # Process data in parallel
    futures = [process_data.remote(x) for x in data]
    
    # Wait for all tasks to complete
    results = ray.get(futures)
    
    # Aggregate results
    total = ray.get(aggregate_results.remote(results))
    
    print(f"✅ Processing complete!")
    print(f"📈 Input sum: {sum(data)}")
    print(f"📈 Output sum: {total}")
    print(f"📈 Processing ratio: {total / sum(data):.2f}")
    
    # Get cluster info
    print(f"\n🔍 Ray cluster info:")
    print(f"   Nodes: {len(ray.nodes())}")
    print(f"   Resources: {ray.cluster_resources()}")
    
    # Clean up
    ray.shutdown()
    print("👋 Ray test completed successfully!")

if __name__ == "__main__":
    main()
