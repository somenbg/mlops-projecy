#!/usr/bin/env python3
"""
Simple ML Training Job for House Price Prediction
This script demonstrates ML training without Ray for simplicity
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os
import argparse
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthetic_data(n_samples: int = 10000) -> pd.DataFrame:
    """Generate synthetic house price data for demonstration"""
    logger.info(f"Generating {n_samples} synthetic house price records")
    
    np.random.seed(42)
    
    data = {
        'sqft': np.random.normal(2000, 500, n_samples).astype(int),
        'bedrooms': np.random.randint(1, 6, n_samples),
        'bathrooms': np.random.randint(1, 4, n_samples),
        'location': np.random.choice(['urban', 'suburban', 'rural'], n_samples),
        'year_built': np.random.randint(1950, 2024, n_samples),
        'condition': np.random.choice(['excellent', 'good', 'fair', 'poor'], n_samples)
    }
    
    # Create price based on features with some noise
    price = (
        data['sqft'] * 100 +
        data['bedrooms'] * 10000 +
        data['bathrooms'] * 5000 +
        (data['year_built'] - 1950) * 200 +
        np.random.normal(0, 20000, n_samples)
    )
    
    data['price'] = np.maximum(price, 50000)  # Minimum price of $50k
    
    return pd.DataFrame(data)

def process_data(data: pd.DataFrame) -> tuple:
    """Process the house price data"""
    logger.info(f"Processing {len(data)} records")
    
    # Handle categorical variables
    categorical_columns = ['location', 'condition']
    label_encoders = {}
    
    for col in categorical_columns:
        if col in data.columns:
            label_encoders[col] = LabelEncoder()
            data[col] = label_encoders[col].fit_transform(data[col])
    
    # Select features
    feature_columns = ['sqft', 'bedrooms', 'bathrooms', 'location', 'year_built', 'condition']
    X = data[feature_columns].values
    y = data['price'].values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, scaler, label_encoders

def train_model(X_train: np.ndarray, y_train: np.ndarray, n_estimators: int = 100, max_depth: int = 10) -> RandomForestRegressor:
    """Train a Random Forest model"""
    logger.info(f"Training model with {len(X_train)} samples")
    
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    return model

def evaluate_model(model: RandomForestRegressor, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    """Evaluate the trained model"""
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    return {
        'mse': mse,
        'rmse': rmse,
        'r2_score': r2
    }

def main():
    parser = argparse.ArgumentParser(description='Simple ML Training for House Price Prediction')
    parser.add_argument('--data-file', type=str, help='Path to CSV data file')
    parser.add_argument('--n-samples', type=int, default=10000, help='Number of synthetic samples to generate')
    parser.add_argument('--n-estimators', type=int, default=100, help='Number of trees in Random Forest')
    parser.add_argument('--max-depth', type=int, default=10, help='Maximum depth of trees')
    parser.add_argument('--test-size', type=float, default=0.2, help='Test set size')
    parser.add_argument('--output-dir', type=str, default='/models', help='Output directory for models')
    
    args = parser.parse_args()
    
    try:
        # Load or generate data
        if args.data_file and os.path.exists(args.data_file):
            logger.info(f"Loading data from {args.data_file}")
            data = pd.read_csv(args.data_file)
        else:
            logger.info("Generating synthetic data...")
            data = generate_synthetic_data(args.n_samples)
        
        logger.info(f"Dataset shape: {data.shape}")
        logger.info(f"Dataset columns: {list(data.columns)}")
        
        # Process data
        logger.info("Processing data...")
        X, y, scaler, label_encoders = process_data(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=42
        )
        
        logger.info(f"Training set size: {len(X_train)}")
        logger.info(f"Test set size: {len(X_test)}")
        
        # Train model
        logger.info("Training model...")
        model = train_model(X_train, y_train, args.n_estimators, args.max_depth)
        
        # Evaluate model
        logger.info("Evaluating model...")
        metrics = evaluate_model(model, X_test, y_test)
        logger.info(f"Model metrics: {metrics}")
        
        # Get feature importance
        feature_names = ['sqft', 'bedrooms', 'bathrooms', 'location', 'year_built', 'condition']
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        logger.info(f"Feature importance: {feature_importance}")
        
        # Save model and scaler
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Save model
        model_path = os.path.join(args.output_dir, 'house_price_model.pkl')
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save scaler
        scaler_path = os.path.join(args.output_dir, 'scaler.pkl')
        joblib.dump(scaler, scaler_path)
        logger.info(f"Scaler saved to {scaler_path}")
        
        # Save label encoders
        encoders_path = os.path.join(args.output_dir, 'label_encoders.pkl')
        joblib.dump(label_encoders, encoders_path)
        logger.info(f"Label encoders saved to {encoders_path}")
        
        logger.info("✅ Training completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
