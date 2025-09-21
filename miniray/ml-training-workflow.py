#!/usr/bin/env python3
"""
ML Training Script for Ray Workflow
This script trains ML models using processed data from the data processing step
"""

import pandas as pd
import numpy as np
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import argparse
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_processed_data(data_dir: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load processed data and metadata from data processing step"""
    logger.info(f"Loading processed data from {data_dir}")
    
    # Load data
    data_path = os.path.join(data_dir, 'processed_data.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Processed data not found at {data_path}")
    
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} records with {len(df.columns)} features")
    
    # Load metadata
    metadata_path = os.path.join(data_dir, 'data_metadata.json')
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Data metadata not found at {metadata_path}")
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    logger.info(f"Loaded metadata: {metadata['total_records']} records, {len(metadata['features'])} features")
    return df, metadata

def prepare_features(df: pd.DataFrame, metadata: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """Prepare features for ML training"""
    logger.info("Preparing features for ML training")
    
    # Get target column
    target_col = metadata['target_column']
    y = df[target_col].values
    
    # Separate categorical and numerical features
    categorical_features = metadata['categorical_features']
    numerical_features = [col for col in metadata['numerical_features'] if col != target_col]
    
    # Encode categorical features
    label_encoders = {}
    X_encoded = df[numerical_features].copy()
    
    for col in categorical_features:
        if col in df.columns:
            le = LabelEncoder()
            X_encoded[col] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le
            logger.info(f"Encoded categorical feature: {col}")
    
    X = X_encoded.values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    logger.info(f"Prepared features: {X_scaled.shape[1]} features, {len(y)} samples")
    
    return X_scaled, y, {
        'label_encoders': label_encoders,
        'scaler': scaler,
        'feature_names': list(X_encoded.columns),
        'categorical_features': categorical_features,
        'numerical_features': numerical_features
    }

def train_models(X: np.ndarray, y: np.ndarray, n_estimators: int = 150, max_depth: int = 12) -> Dict[str, Any]:
    """Train multiple ML models"""
    logger.info("Training ML models")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Define models
    models = {
        'random_forest': RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        ),
        'gradient_boosting': GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        ),
        'linear_regression': LinearRegression()
    }
    
    # Train models
    trained_models = {}
    model_metrics = {}
    
    for name, model in models.items():
        logger.info(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        metrics = {
            'mse': mse,
            'rmse': rmse,
            'r2_score': r2,
            'mae': mae
        }
        
        trained_models[name] = model
        model_metrics[name] = metrics
        
        logger.info(f"{name} - R²: {r2:.4f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}")
    
    # Select best model
    best_model_name = max(model_metrics.keys(), key=lambda k: model_metrics[k]['r2_score'])
    best_model = trained_models[best_model_name]
    best_metrics = model_metrics[best_model_name]
    
    logger.info(f"Best model: {best_model_name} (R²: {best_metrics['r2_score']:.4f})")
    
    return {
        'models': trained_models,
        'metrics': model_metrics,
        'best_model_name': best_model_name,
        'best_model': best_model,
        'best_metrics': best_metrics,
        'X_test': X_test,
        'y_test': y_test
    }

def save_models_and_artifacts(training_results: Dict[str, Any], preprocessing_info: Dict[str, Any], 
                            output_dir: str, workflow_id: str) -> Dict[str, Any]:
    """Save trained models and artifacts"""
    logger.info(f"Saving models and artifacts to {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save all models
    models_dir = os.path.join(output_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    for name, model in training_results['models'].items():
        model_path = os.path.join(models_dir, f'{name}_model.pkl')
        joblib.dump(model, model_path)
        logger.info(f"Saved {name} model to {model_path}")
    
    # Save preprocessing artifacts
    artifacts_dir = os.path.join(output_dir, 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Save scaler
    scaler_path = os.path.join(artifacts_dir, 'scaler.pkl')
    joblib.dump(preprocessing_info['scaler'], scaler_path)
    
    # Save label encoders
    encoders_path = os.path.join(artifacts_dir, 'label_encoders.pkl')
    joblib.dump(preprocessing_info['label_encoders'], encoders_path)
    
    # Save feature names
    feature_names_path = os.path.join(artifacts_dir, 'feature_names.json')
    with open(feature_names_path, 'w') as f:
        json.dump(preprocessing_info['feature_names'], f, indent=2)
    
    # Save training results
    results_path = os.path.join(output_dir, 'training_results.json')
    training_summary = {
        'workflow_id': workflow_id,
        'best_model': training_results['best_model_name'],
        'best_metrics': training_results['best_metrics'],
        'all_metrics': training_results['metrics'],
        'feature_count': len(preprocessing_info['feature_names']),
        'training_samples': len(training_results['X_test']) + len(training_results['X_test']) * 4,  # Approximate
        'test_samples': len(training_results['X_test'])
    }
    
    with open(results_path, 'w') as f:
        json.dump(training_summary, f, indent=2)
    
    # Create workflow status
    status_file = os.path.join(output_dir, 'workflow_status.json')
    workflow_status = {
        'workflow_id': workflow_id,
        'step': 'ml_training',
        'status': 'completed',
        'best_model': training_results['best_model_name'],
        'best_r2_score': training_results['best_metrics']['r2_score'],
        'output_files': [
            'models/',
            'artifacts/',
            'training_results.json',
            'workflow_status.json'
        ],
        'next_step': 'model_serving',
        'summary': training_summary
    }
    
    with open(status_file, 'w') as f:
        json.dump(workflow_status, f, indent=2)
    
    logger.info(f"Training results saved to {results_path}")
    logger.info(f"Workflow status saved to {status_file}")
    
    return training_summary

def main():
    parser = argparse.ArgumentParser(description='ML Training for Ray Workflow')
    parser.add_argument('--data-dir', type=str, default='/data', help='Directory containing processed data')
    parser.add_argument('--output-dir', type=str, default='/models', help='Output directory for models')
    parser.add_argument('--n-estimators', type=int, default=150, help='Number of estimators for tree models')
    parser.add_argument('--max-depth', type=int, default=12, help='Maximum depth for tree models')
    parser.add_argument('--workflow-id', type=str, default='workflow-001', help='Workflow ID for tracking')
    
    args = parser.parse_args()
    
    try:
        logger.info(f"🚀 Starting ML training workflow: {args.workflow_id}")
        
        # Step 1: Load processed data
        df, metadata = load_processed_data(args.data_dir)
        
        # Step 2: Prepare features
        X, y, preprocessing_info = prepare_features(df, metadata)
        
        # Step 3: Train models
        training_results = train_models(X, y, args.n_estimators, args.max_depth)
        
        # Step 4: Save models and artifacts
        summary = save_models_and_artifacts(training_results, preprocessing_info, args.output_dir, args.workflow_id)
        
        logger.info("✅ ML training completed successfully!")
        logger.info(f"🏆 Best model: {summary['best_model']} (R²: {summary['best_metrics']['r2_score']:.4f})")
        logger.info(f"📊 Trained {len(training_results['models'])} models")
        logger.info(f"📁 Output directory: {args.output_dir}")
        logger.info(f"🔄 Next step: Model serving")
        
    except Exception as e:
        logger.error(f"❌ ML training failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
