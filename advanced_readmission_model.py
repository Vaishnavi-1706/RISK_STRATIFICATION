#!/usr/bin/env python3
"""
Advanced Patient Readmission Risk Prediction Model
Healthcare Risk Stratification - Machine Learning Pipeline
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from sklearn.multioutput import MultiOutputClassifier
import xgboost as xgb
import lightgbm as lgb
import warnings
import joblib
import os
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import randint, uniform

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class AdvancedReadmissionModel:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.best_model = None
        self.best_score = 0
        self.feature_importance = None
        self.test_predictions = None
        self.test_probabilities = None
        
    def load_and_prepare_data(self):
        """Load and prepare the dataset for readmission prediction"""
        logger.info("Loading dataset for readmission prediction...")
        
        # Load the dataset
        df = pd.read_csv('index.csv')
        logger.info(f"Dataset loaded: {df.shape}")
        
        # Create readmission target based on risk scores
        # High risk patients (30-day risk >= 60) are considered likely to be readmitted
        df['READMISSION_RISK'] = (df['RISK_30D'] >= 60).astype(int)
        
        # Separate features and target
        feature_columns = [col for col in df.columns if col not in [
            'DESYNPUF_ID', 'RISK_30D', 'RISK_60D', 'RISK_90D', 'RISK_LABEL', 
            'TOP_3_FEATURES', 'AI_RECOMMENDATIONS', 'EMAIL', 'SHAP_EXPLANATION',
            'READMISSION_RISK'
        ]]
        
        X = df[feature_columns].copy()
        y = df['READMISSION_RISK']
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # Convert categorical variables
        categorical_cols = X.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            X[col] = self.label_encoder.fit_transform(X[col].astype(str))
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        logger.info(f"Features shape: {X_scaled.shape}")
        logger.info(f"Target distribution: {y.value_counts()}")
        logger.info(f"Readmission rate: {y.mean():.2%}")
        
        return X_scaled, y, feature_columns
    
    def define_models_and_params(self):
        """Define various models with their hyperparameter grids"""
        models = {
            'XGBoost': {
                'model': xgb.XGBClassifier(random_state=42, eval_metric='logloss'),
                'params': {
                    'n_estimators': [100, 200, 300, 500],
                    'max_depth': [3, 5, 7, 9],
                    'learning_rate': [0.01, 0.05, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0],
                    'reg_alpha': [0, 0.1, 0.5],
                    'reg_lambda': [0, 0.1, 0.5],
                    'min_child_weight': [1, 3, 5]
                }
            },
            'LightGBM': {
                'model': lgb.LGBMClassifier(random_state=42, verbose=-1),
                'params': {
                    'n_estimators': [100, 200, 300, 500],
                    'max_depth': [3, 5, 7, 9],
                    'learning_rate': [0.01, 0.05, 0.1, 0.2],
                    'num_leaves': [31, 50, 100, 200],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0],
                    'reg_alpha': [0, 0.1, 0.5],
                    'reg_lambda': [0, 0.1, 0.5]
                }
            },
            'RandomForest': {
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200, 300, 500],
                    'max_depth': [10, 20, 30, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', None],
                    'class_weight': ['balanced', 'balanced_subsample', None]
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'learning_rate': [0.01, 0.05, 0.1, 0.2],
                    'max_depth': [3, 5, 7, 9],
                    'min_samples_split': [2, 5, 10],
                    'subsample': [0.8, 0.9, 1.0]
                }
            },
            'ExtraTrees': {
                'model': ExtraTreesClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200, 300, 500],
                    'max_depth': [10, 20, 30, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', None],
                    'class_weight': ['balanced', 'balanced_subsample', None]
                }
            },
            'LogisticRegression': {
                'model': LogisticRegression(random_state=42, max_iter=1000),
                'params': {
                    'C': [0.001, 0.01, 0.1, 1, 10, 100],
                    'penalty': ['l1', 'l2'],
                    'solver': ['liblinear', 'saga'],
                    'class_weight': ['balanced', None]
                }
            }
        }
        
        return models
    
    def train_and_evaluate_models(self, X, y):
        """Train and evaluate multiple models with hyperparameter tuning"""
        logger.info("Starting model training and evaluation...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        models = self.define_models_and_params()
        results = {}
        
        for name, model_info in models.items():
            logger.info(f"Training {name}...")
            
            try:
                # Use RandomizedSearchCV for faster tuning
                random_search = RandomizedSearchCV(
                    model_info['model'],
                    model_info['params'],
                    n_iter=50,  # Number of parameter combinations to try
                    cv=5,
                    scoring='accuracy',
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
                y_prob = best_model.predict_proba(X_test)[:, 1]
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                auc = roc_auc_score(y_test, y_prob)
                
                results[name] = {
                    'model': best_model,
                    'best_params': random_search.best_params_,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'auc': auc,
                    'best_score': random_search.best_score_,
                    'predictions': y_pred,
                    'probabilities': y_prob
                }
                
                logger.info(f"{name} - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}, Best CV Score: {random_search.best_score_:.4f}")
                
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
                continue
        
        return results, X_test, y_test
    
    def select_best_model(self, results):
        """Select the best performing model"""
        best_model_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
        self.best_model = results[best_model_name]['model']
        self.best_score = results[best_model_name]['accuracy']
        
        # Store test predictions for the best model
        self.test_predictions = results[best_model_name]['predictions']
        self.test_probabilities = results[best_model_name]['probabilities']
        
        logger.info(f"Best model: {best_model_name} with accuracy: {self.best_score:.4f}")
        
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
    
    def create_evaluation_plots(self, y_test, save_path='models/'):
        """Create evaluation plots and save them"""
        os.makedirs(save_path, exist_ok=True)
        
        # Confusion Matrix
        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_test, self.test_predictions)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['No Readmission', 'Readmission'],
                   yticklabels=['No Readmission', 'Readmission'])
        plt.title('Confusion Matrix - Readmission Prediction')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(f'{save_path}confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # ROC Curve
        plt.figure(figsize=(8, 6))
        fpr, tpr, _ = roc_curve(y_test, self.test_probabilities)
        auc_score = roc_auc_score(y_test, self.test_probabilities)
        
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {auc_score:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve - Readmission Prediction')
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(f'{save_path}roc_curve.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Feature Importance Plot
        if self.feature_importance is not None:
            plt.figure(figsize=(12, 8))
            top_features = self.feature_importance.head(15)
            sns.barplot(data=top_features, x='importance', y='feature')
            plt.title('Top 15 Feature Importances - Readmission Prediction')
            plt.xlabel('Importance')
            plt.tight_layout()
            plt.savefig(f'{save_path}feature_importance.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        logger.info(f"Evaluation plots saved to {save_path}")
    
    def save_model(self, model_name, feature_names):
        """Save the trained model and related files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Save the best model
        model_path = f'models/readmission_model_{timestamp}.pkl'
        joblib.dump(self.best_model, model_path)
        
        # Save scaler
        scaler_path = f'models/readmission_scaler_{timestamp}.pkl'
        joblib.dump(self.scaler, scaler_path)
        
        # Save feature importance
        if self.feature_importance is not None:
            importance_path = f'models/readmission_feature_importance_{timestamp}.csv'
            self.feature_importance.to_csv(importance_path, index=False)
        
        # Save model info
        model_info = {
            'model_name': model_name,
            'best_score': self.best_score,
            'timestamp': timestamp,
            'model_path': model_path,
            'scaler_path': scaler_path,
            'feature_names': feature_names
        }
        
        info_path = f'models/readmission_model_info_{timestamp}.txt'
        with open(info_path, 'w') as f:
            for key, value in model_info.items():
                f.write(f"{key}: {value}\n")
        
        logger.info(f"Model saved successfully!")
        logger.info(f"Model path: {model_path}")
        logger.info(f"Scaler path: {scaler_path}")
        
        return model_info
    
    def generate_performance_report(self, results, X_test, y_test):
        """Generate a comprehensive performance report"""
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE PERFORMANCE REPORT")
        logger.info("="*80)
        
        # Overall best model
        best_name, best_result = self.select_best_model(results)
        
        logger.info(f"\n🏆 BEST MODEL: {best_name}")
        logger.info(f"Test Accuracy: {best_result['accuracy']:.4f}")
        logger.info(f"Cross-Validation Score: {best_result['best_score']:.4f}")
        logger.info(f"Precision: {best_result['precision']:.4f}")
        logger.info(f"Recall: {best_result['recall']:.4f}")
        logger.info(f"F1-Score: {best_result['f1']:.4f}")
        logger.info(f"AUC-ROC: {best_result['auc']:.4f}")
        
        # Model comparison
        logger.info(f"\n📈 MODEL COMPARISON:")
        comparison_df = pd.DataFrame({
            'Model': list(results.keys()),
            'Accuracy': [results[name]['accuracy'] for name in results.keys()],
            'Precision': [results[name]['precision'] for name in results.keys()],
            'Recall': [results[name]['recall'] for name in results.keys()],
            'F1-Score': [results[name]['f1'] for name in results.keys()],
            'AUC-ROC': [results[name]['auc'] for name in results.keys()]
        }).sort_values('Accuracy', ascending=False)
        
        logger.info(comparison_df.to_string(index=False))
        
        # Confusion Matrix
        logger.info(f"\n📊 CONFUSION MATRIX:")
        cm = confusion_matrix(y_test, self.test_predictions)
        logger.info(f"True Negatives: {cm[0,0]}")
        logger.info(f"False Positives: {cm[0,1]}")
        logger.info(f"False Negatives: {cm[1,0]}")
        logger.info(f"True Positives: {cm[1,1]}")
        
        # Classification Report
        logger.info(f"\n📋 CLASSIFICATION REPORT:")
        report = classification_report(y_test, self.test_predictions, 
                                     target_names=['No Readmission', 'Readmission'])
        logger.info(report)
        
        # Feature importance
        if self.feature_importance is not None:
            logger.info(f"\n🔍 TOP 15 FEATURES:")
            for i, row in self.feature_importance.head(15).iterrows():
                logger.info(f"  {row['feature']:25s}: {row['importance']:.4f}")
        
        return best_name, best_result, comparison_df

def main():
    """Main training function"""
    logger.info("🚀 Starting Advanced Readmission Risk Prediction Model Training")
    logger.info("="*80)
    
    # Initialize the model trainer
    trainer = AdvancedReadmissionModel()
    
    # Load and prepare data
    X, y, feature_names = trainer.load_and_prepare_data()
    
    # Train and evaluate models
    results, X_test, y_test = trainer.train_and_evaluate_models(X, y)
    
    # Generate performance report
    best_name, best_result, comparison_df = trainer.generate_performance_report(results, X_test, y_test)
    
    # Get feature importance
    trainer.get_feature_importance(feature_names)
    
    # Create evaluation plots
    trainer.create_evaluation_plots(y_test)
    
    # Save the best model
    model_info = trainer.save_model(best_name, feature_names)
    
    logger.info("\n" + "="*80)
    logger.info("🎉 TRAINING COMPLETED SUCCESSFULLY!")
    logger.info("="*80)
    
    # Final summary
    logger.info(f"📊 Final Results:")
    logger.info(f"   Best Model: {best_name}")
    logger.info(f"   Test Accuracy: {best_result['accuracy']:.4f}")
    logger.info(f"   Target Accuracy: 95%")
    logger.info(f"   Achieved Accuracy: {best_result['accuracy']*100:.2f}%")
    
    if best_result['accuracy'] >= 0.95:
        logger.info("✅ Target accuracy achieved!")
    elif best_result['accuracy'] >= 0.90:
        logger.info("✅ Excellent accuracy achieved!")
    elif best_result['accuracy'] >= 0.85:
        logger.info("✅ Good accuracy achieved!")
    else:
        logger.info("⚠️ Accuracy can be improved with more training")
    
    # Save comparison results
    comparison_df.to_csv('models/model_comparison_results.csv', index=False)
    logger.info("📄 Model comparison results saved to models/model_comparison_results.csv")
    
    return trainer, results, comparison_df

if __name__ == "__main__":
    trainer, results, comparison_df = main()
