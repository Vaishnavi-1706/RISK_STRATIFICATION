#!/usr/bin/env python3
"""
Fast Model Training with Hyperparameter Tuning
Healthcare Risk Stratification - Optimized for Speed and Accuracy
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import warnings
import joblib
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class FastRiskModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_score = 0
        self.feature_importance = None
        
    def load_and_prepare_data(self):
        """Load and prepare the dataset efficiently"""
        logger.info("Loading dataset...")
        
        # Load the dataset
        df = pd.read_csv('index.csv')
        logger.info(f"Dataset loaded: {df.shape}")
        
        # Separate features and targets
        feature_columns = [col for col in df.columns if col not in ['DESYNPUF_ID', 'RISK_30D', 'RISK_60D', 'RISK_90D', 'RISK_LABEL']]
        
        X = df[feature_columns].copy()
        y_30d = df['RISK_30D']
        y_60d = df['RISK_60D']
        y_90d = df['RISK_90D']
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Combine targets for multi-output regression
        y_combined = np.column_stack([y_30d, y_60d, y_90d])
        
        logger.info(f"Features shape: {X_scaled.shape}")
        logger.info(f"Targets shape: {y_combined.shape}")
        
        return X_scaled, y_combined, feature_columns
    
    def define_models(self):
        """Define optimized models with focused hyperparameter grids"""
        models = {
            'XGBoost': {
                'model': xgb.XGBRegressor(random_state=42, n_jobs=-1),
                'params': {
                    'n_estimators': [200, 300, 500],
                    'max_depth': [5, 7, 9],
                    'learning_rate': [0.05, 0.1, 0.2],
                    'subsample': [0.8, 0.9],
                    'colsample_bytree': [0.8, 0.9],
                    'reg_alpha': [0, 0.1],
                    'reg_lambda': [0, 0.1]
                }
            },
            'LightGBM': {
                'model': lgb.LGBMRegressor(random_state=42, verbose=-1, n_jobs=-1),
                'params': {
                    'n_estimators': [200, 300, 500],
                    'max_depth': [5, 7, 9],
                    'learning_rate': [0.05, 0.1, 0.2],
                    'num_leaves': [31, 50, 100],
                    'subsample': [0.8, 0.9],
                    'colsample_bytree': [0.8, 0.9]
                }
            },
            'RandomForest': {
                'model': RandomForestRegressor(random_state=42, n_jobs=-1),
                'params': {
                    'n_estimators': [200, 300, 500],
                    'max_depth': [15, 20, 25],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2],
                    'max_features': ['sqrt', 'log2']
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingRegressor(random_state=42),
                'params': {
                    'n_estimators': [200, 300],
                    'learning_rate': [0.05, 0.1, 0.2],
                    'max_depth': [5, 7, 9],
                    'min_samples_split': [2, 5],
                    'subsample': [0.8, 0.9]
                }
            }
        }
        
        return models
    
    def train_and_evaluate_models(self, X, y):
        """Train and evaluate models efficiently"""
        logger.info("Starting model training and evaluation...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        models = self.define_models()
        results = {}
        
        for name, model_info in models.items():
            logger.info(f"Training {name}...")
            
            try:
                # Use RandomizedSearchCV with fewer iterations for speed
                random_search = RandomizedSearchCV(
                    model_info['model'],
                    model_info['params'],
                    n_iter=20,  # Reduced for speed
                    cv=3,       # Reduced for speed
                    scoring='r2',
                    n_jobs=-1,
                    random_state=42,
                    verbose=0
                )
                
                # Train the model
                random_search.fit(X_train, y_train)
                
                # Get best model
                best_model = random_search.best_estimator_
                
                # Evaluate on test set
                y_pred = best_model.predict(X_test)
                
                # Calculate metrics for each target
                metrics = {}
                target_names = ['RISK_30D', 'RISK_60D', 'RISK_90D']
                
                for i, target in enumerate(target_names):
                    mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
                    mse = mean_squared_error(y_test[:, i], y_pred[:, i])
                    r2 = r2_score(y_test[:, i], y_pred[:, i])
                    
                    metrics[target] = {
                        'MAE': mae,
                        'MSE': mse,
                        'R2': r2
                    }
                
                # Average R2 score across all targets
                avg_r2 = np.mean([metrics[target]['R2'] for target in target_names])
                
                results[name] = {
                    'model': best_model,
                    'best_params': random_search.best_params_,
                    'metrics': metrics,
                    'avg_r2': avg_r2,
                    'best_score': random_search.best_score_
                }
                
                logger.info(f"{name} - Avg R²: {avg_r2:.4f}, Best CV Score: {random_search.best_score_:.4f}")
                
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
                continue
        
        return results, X_test, y_test
    
    def select_best_model(self, results):
        """Select the best performing model"""
        best_model_name = max(results.keys(), key=lambda x: results[x]['avg_r2'])
        self.best_model = results[best_model_name]['model']
        self.best_score = results[best_model_name]['avg_r2']
        
        logger.info(f"Best model: {best_model_name} with R² score: {self.best_score:.4f}")
        
        return best_model_name, results[best_model_name]
    
    def get_feature_importance(self, feature_names):
        """Extract feature importance from the best model"""
        if hasattr(self.best_model, 'feature_importances_'):
            importance = self.best_model.feature_importances_
            self.feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            logger.info("Top 10 most important features:")
            logger.info(self.feature_importance.head(10))
        
        return self.feature_importance
    
    def save_model(self, model_name):
        """Save the trained model and related files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Save the best model
        model_path = f'models/best_risk_model_{timestamp}.pkl'
        joblib.dump(self.best_model, model_path)
        
        # Save scaler
        scaler_path = f'models/scaler_{timestamp}.pkl'
        joblib.dump(self.scaler, scaler_path)
        
        # Save feature importance
        if self.feature_importance is not None:
            importance_path = f'models/feature_importance_{timestamp}.csv'
            self.feature_importance.to_csv(importance_path, index=False)
        
        # Save model info
        model_info = {
            'model_name': model_name,
            'best_score': self.best_score,
            'timestamp': timestamp,
            'model_path': model_path,
            'scaler_path': scaler_path
        }
        
        info_path = f'models/model_info_{timestamp}.txt'
        with open(info_path, 'w') as f:
            for key, value in model_info.items():
                f.write(f"{key}: {value}\n")
        
        logger.info(f"Model saved successfully!")
        logger.info(f"Model path: {model_path}")
        logger.info(f"Scaler path: {scaler_path}")
        
        return model_info
    
    def generate_performance_report(self, results, X_test, y_test):
        """Generate a comprehensive performance report"""
        logger.info("\n" + "="*60)
        logger.info("PERFORMANCE REPORT")
        logger.info("="*60)
        
        # Overall best model
        best_name, best_result = self.select_best_model(results)
        
        logger.info(f"\n🏆 BEST MODEL: {best_name}")
        logger.info(f"Average R² Score: {best_result['avg_r2']:.4f}")
        logger.info(f"Cross-Validation Score: {best_result['best_score']:.4f}")
        
        # Detailed metrics for best model
        logger.info(f"\n📊 DETAILED METRICS FOR {best_name}:")
        for target, metrics in best_result['metrics'].items():
            logger.info(f"{target}:")
            logger.info(f"  MAE: {metrics['MAE']:.3f}")
            logger.info(f"  MSE: {metrics['MSE']:.3f}")
            logger.info(f"  R²:  {metrics['R2']:.4f}")
        
        # Model comparison
        logger.info(f"\n📈 MODEL COMPARISON:")
        for name, result in results.items():
            logger.info(f"{name:15s}: R² = {result['avg_r2']:.4f}")
        
        # Feature importance
        if self.feature_importance is not None:
            logger.info(f"\n🔍 TOP 10 FEATURES:")
            for i, row in self.feature_importance.head(10).iterrows():
                logger.info(f"  {row['feature']:20s}: {row['importance']:.4f}")
        
        return best_name, best_result

def main():
    """Main training function"""
    logger.info("🚀 Starting Fast Model Training")
    logger.info("="*60)
    
    # Initialize the model trainer
    trainer = FastRiskModel()
    
    # Load and prepare data
    X, y, feature_names = trainer.load_and_prepare_data()
    
    # Train and evaluate models
    results, X_test, y_test = trainer.train_and_evaluate_models(X, y)
    
    # Generate performance report
    best_name, best_result = trainer.generate_performance_report(results, X_test, y_test)
    
    # Get feature importance
    trainer.get_feature_importance(feature_names)
    
    # Save the best model
    model_info = trainer.save_model(best_name)
    
    logger.info("\n" + "="*60)
    logger.info("🎉 TRAINING COMPLETED SUCCESSFULLY!")
    logger.info("="*60)
    
    # Final summary
    logger.info(f"📊 Final Results:")
    logger.info(f"   Best Model: {best_name}")
    logger.info(f"   Average R² Score: {best_result['avg_r2']:.4f}")
    logger.info(f"   Target Accuracy: ~95% (R² = 0.95)")
    logger.info(f"   Achieved Accuracy: {best_result['avg_r2']*100:.2f}%")
    
    if best_result['avg_r2'] >= 0.95:
        logger.info("✅ Target accuracy achieved!")
    elif best_result['avg_r2'] >= 0.90:
        logger.info("✅ Excellent accuracy achieved!")
    elif best_result['avg_r2'] >= 0.85:
        logger.info("✅ Good accuracy achieved!")
    else:
        logger.info("⚠️ Accuracy can be improved with more training")
    
    return trainer, results

if __name__ == "__main__":
    trainer, results = main()
