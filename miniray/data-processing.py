#!/usr/bin/env python3
"""
Data Processing Script for Ray Workflow
This script processes raw data and prepares it for ML training
"""

import pandas as pd
import numpy as np
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_raw_data(n_samples: int = 10000) -> pd.DataFrame:
    """Generate raw synthetic house price data"""
    logger.info(f"Generating {n_samples} raw synthetic house price records")
    
    np.random.seed(42)
    
    # Generate raw data with more noise and inconsistencies
    data = {
        'sqft': np.random.normal(2000, 800, n_samples).astype(int),
        'bedrooms': np.random.randint(1, 8, n_samples),  # More bedrooms
        'bathrooms': np.random.randint(1, 6, n_samples),  # More bathrooms
        'location': np.random.choice(['urban', 'suburban', 'rural', 'downtown'], n_samples),
        'year_built': np.random.randint(1900, 2024, n_samples),
        'condition': np.random.choice(['excellent', 'good', 'fair', 'poor', 'needs_work'], n_samples),
        'garage': np.random.choice([0, 1, 2, 3], n_samples),
        'pool': np.random.choice([0, 1], n_samples),
        'basement': np.random.choice([0, 1], n_samples)
    }
    
    # Create price with more complex relationships and noise
    price = (
        data['sqft'] * 120 +  # Base price per sqft
        data['bedrooms'] * 15000 +
        data['bathrooms'] * 8000 +
        (data['year_built'] - 1900) * 300 +  # Age factor
        data['garage'] * 10000 +
        data['pool'] * 25000 +
        data['basement'] * 15000 +
        np.random.normal(0, 50000, n_samples)  # More noise
    )
    
    # Add location premium
    location_multiplier = {
        'downtown': 1.3,
        'urban': 1.1,
        'suburban': 1.0,
        'rural': 0.8
    }
    
    for i, loc in enumerate(data['location']):
        price[i] *= location_multiplier[loc]
    
    data['price'] = np.maximum(price, 30000)  # Minimum price
    
    # Add some missing values and outliers
    missing_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    for col in ['bedrooms', 'bathrooms']:
        # Convert to float first to allow NaN values
        data[col] = data[col].astype(float)
        data[col][missing_indices] = np.nan
    
    # Add outliers
    outlier_indices = np.random.choice(n_samples, size=int(n_samples * 0.02), replace=False)
    data['price'][outlier_indices] *= np.random.uniform(3, 8, len(outlier_indices))
    
    return pd.DataFrame(data)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw data"""
    logger.info(f"Cleaning data: {len(df)} records")
    
    # Remove outliers (prices > 3 standard deviations from mean)
    price_mean = df['price'].mean()
    price_std = df['price'].std()
    df = df[df['price'] <= price_mean + 3 * price_std]
    
    # Fill missing values
    df['bedrooms'] = df['bedrooms'].fillna(df['bedrooms'].median())
    df['bathrooms'] = df['bathrooms'].fillna(df['bathrooms'].median())
    
    # Convert to appropriate types
    df['bedrooms'] = df['bedrooms'].astype(int)
    df['bathrooms'] = df['bathrooms'].astype(int)
    df['garage'] = df['garage'].astype(int)
    df['pool'] = df['pool'].astype(int)
    df['basement'] = df['basement'].astype(int)
    
    logger.info(f"Cleaned data: {len(df)} records remaining")
    return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer new features"""
    logger.info("Engineering features")
    
    # Age of house
    df['house_age'] = 2024 - df['year_built']
    
    # Price per square foot (handle division by zero)
    df['price_per_sqft'] = df['price'] / df['sqft'].replace(0, 1)  # Replace 0 with 1 to avoid division by zero
    # Replace any infinite values with NaN, then fill with median
    df['price_per_sqft'] = df['price_per_sqft'].replace([np.inf, -np.inf], np.nan)
    df['price_per_sqft'] = df['price_per_sqft'].fillna(df['price_per_sqft'].median())
    
    # Total rooms
    df['total_rooms'] = df['bedrooms'] + df['bathrooms']
    
    # Luxury features score
    df['luxury_score'] = df['pool'] + df['basement'] + (df['garage'] > 1).astype(int)
    
    # Size categories
    df['size_category'] = pd.cut(df['sqft'], 
                                bins=[0, 1500, 2500, 3500, float('inf')], 
                                labels=['small', 'medium', 'large', 'xlarge'])
    
    # Age categories
    df['age_category'] = pd.cut(df['house_age'], 
                               bins=[0, 10, 30, 50, float('inf')], 
                               labels=['new', 'modern', 'old', 'historic'])
    
    # Clean up any remaining infinite or extremely large values
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        # Replace extremely large values (greater than 1e10) with median
        df[col] = df[col].where(df[col].abs() < 1e10, df[col].median())
        df[col] = df[col].fillna(df[col].median())
    
    logger.info("Feature engineering completed")
    return df

def save_processed_data(df: pd.DataFrame, output_dir: str) -> Dict[str, Any]:
    """Save processed data and metadata"""
    logger.info(f"Saving processed data to {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save processed data
    data_path = os.path.join(output_dir, 'processed_data.csv')
    df.to_csv(data_path, index=False)
    
    # Save metadata
    metadata = {
        'total_records': len(df),
        'features': list(df.columns),
        'categorical_features': ['location', 'condition', 'size_category', 'age_category'],
        'numerical_features': [col for col in df.columns if col not in ['location', 'condition', 'size_category', 'age_category']],
        'target_column': 'price',
        'data_quality': {
            'missing_values': df.isnull().sum().to_dict(),
            'outliers_removed': True,
            'features_engineered': True
        }
    }
    
    metadata_path = os.path.join(output_dir, 'data_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Data saved to {data_path}")
    logger.info(f"Metadata saved to {metadata_path}")
    
    return metadata

def main():
    parser = argparse.ArgumentParser(description='Data Processing for Ray Workflow')
    parser.add_argument('--n-samples', type=int, default=10000, help='Number of samples to generate')
    parser.add_argument('--output-dir', type=str, default='/data', help='Output directory for processed data')
    parser.add_argument('--workflow-id', type=str, default='workflow-001', help='Workflow ID for tracking')
    
    args = parser.parse_args()
    
    try:
        logger.info(f"🚀 Starting data processing workflow: {args.workflow_id}")
        
        # Step 1: Generate raw data
        raw_data = generate_raw_data(args.n_samples)
        logger.info(f"Generated {len(raw_data)} raw records")
        
        # Step 2: Clean data
        cleaned_data = clean_data(raw_data)
        logger.info(f"Cleaned data: {len(cleaned_data)} records")
        
        # Step 3: Engineer features
        processed_data = engineer_features(cleaned_data)
        logger.info(f"Feature engineering completed: {len(processed_data.columns)} features")
        
        # Step 4: Save processed data
        metadata = save_processed_data(processed_data, args.output_dir)
        
        # Step 5: Create workflow status file
        status_file = os.path.join(args.output_dir, 'workflow_status.json')
        workflow_status = {
            'workflow_id': args.workflow_id,
            'step': 'data_processing',
            'status': 'completed',
            'output_files': [
                'processed_data.csv',
                'data_metadata.json',
                'workflow_status.json'
            ],
            'next_step': 'ml_training',
            'metadata': metadata
        }
        
        with open(status_file, 'w') as f:
            json.dump(workflow_status, f, indent=2)
        
        logger.info("✅ Data processing completed successfully!")
        logger.info(f"📊 Processed {metadata['total_records']} records with {len(metadata['features'])} features")
        logger.info(f"📁 Output directory: {args.output_dir}")
        logger.info(f"🔄 Next step: ML training")
        
    except Exception as e:
        logger.error(f"❌ Data processing failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
