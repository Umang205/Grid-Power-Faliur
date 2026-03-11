import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import joblib
import warnings
warnings.filterwarnings('ignore')

class PowerGridFailurePredictor:
    def __init__(self):
        self.model = None
        self.reason_model = None
        self.features = None
        self.target = None
        self.reason_features = None
        self.encoders = {}
        self.grid_failure_reasons = [
            'animal intervention', 'overload', 'weather rainstrom', 
            'weather rainstorm', 'equipment failure'
        ]
    
    def load_data(self, filepath):
        """Load and preprocess the data"""
        df = pd.read_excel(filepath)
        
        # Clean and standardize reason column
        df['reason'] = df['reason'].str.lower().str.strip().fillna('unknown')
        
        # Create target variable
        df['grid_failure'] = df['reason'].apply(
            lambda x: 1 if any(gfr in x for gfr in self.grid_failure_reasons) else 0
        )
        
        # Convert time columns and calculate duration
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
        df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
        
        # Drop rows with invalid dates
        df = df.dropna(subset=['start_time', 'end_time'])
        
        df['duration_minutes'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60
        
        # Extract time features
        df['start_hour'] = df['start_time'].dt.hour
        df['start_dayofweek'] = df['start_time'].dt.dayofweek
        df['start_month'] = df['start_time'].dt.month
        
        return df
    
    def engineer_features(self, df):
        """Feature engineering and encoding"""
        # Encode categorical variables
        cat_cols = ['power_plant', 'area', 'reason']
        for col in cat_cols:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col])
            self.encoders[col] = le
        
        # Define features for failure prediction
        num_cols = ['duration_minutes', 'start_hour', 'start_dayofweek', 'start_month']
        encoded_cat_cols = [col + '_encoded' for col in ['power_plant', 'area']]
        
        self.features = num_cols + encoded_cat_cols
        self.target = 'grid_failure'
        
        # Define features for reason prediction
        self.reason_features = num_cols + encoded_cat_cols
        self.reason_target = 'reason_encoded'
        
        return df
    
    def train_model(self, X_train, y_train, X_reason_train, y_reason_train):
        """Train models with hyperparameter tuning"""
        # Preprocessing pipeline
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())])
        
        preprocessor = ColumnTransformer(
            transformers=[('num', numeric_transformer, X_train.columns)])
        
        # Train failure prediction model
        print("\nTraining failure prediction model...")
        self.model = self._train_classifier(X_train, y_train, preprocessor)
        
        # Train reason prediction model
        print("\nTraining reason prediction model...")
        self.reason_model = self._train_classifier(X_reason_train, y_reason_train, preprocessor)
    
    def _train_classifier(self, X_train, y_train, preprocessor):
        """Helper method to train a classifier"""
        models = [
            {
                'name': 'RandomForest',
                'estimator': RandomForestClassifier(random_state=42),
                'params': {
                    'classifier__n_estimators': [100, 200],
                    'classifier__max_depth': [None, 10, 20],
                    'classifier__min_samples_split': [2, 5],
                    'classifier__min_samples_leaf': [1, 2]
                }
            },
            {
                'name': 'GradientBoosting',
                'estimator': GradientBoostingClassifier(random_state=42),
                'params': {
                    'classifier__n_estimators': [100, 200],
                    'classifier__learning_rate': [0.05, 0.1],
                    'classifier__max_depth': [3, 5]
                }
            }
        ]
        
        best_model = None
        best_score = 0
        
        for model in models:
            print(f"Training {model['name']}...")
            pipeline = Pipeline(steps=[
                ('preprocessor', preprocessor),
                ('feature_selection', SelectKBest(mutual_info_classif, k='all')),
                ('classifier', model['estimator'])])
            
            scoring = 'f1' if len(np.unique(y_train)) == 2 else 'accuracy'
            
            grid_search = GridSearchCV(
                pipeline,
                param_grid=model['params'],
                cv=5,
                scoring=scoring,
                n_jobs=-1,
                verbose=1,
                error_score='raise')
            
            grid_search.fit(X_train, y_train)
            
            if grid_search.best_score_ > best_score:
                best_score = grid_search.best_score_
                best_model = grid_search.best_estimator_
                print(f"New best model: {model['name']} with {scoring} score: {best_score:.4f}")
        
        print("\nBest model parameters:")
        print(best_model.named_steps['classifier'])
        
        return best_model
    
    def evaluate_model(self, X_test, y_test, X_reason_test, y_reason_test):
        """Evaluate model performance"""
        # Evaluate failure prediction model
        print("\nFailure Prediction Model Evaluation:")
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        print(classification_report(y_test, y_pred))
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
        
        # Evaluate reason prediction model
        print("\nReason Prediction Model Evaluation:")
        y_reason_pred = self.reason_model.predict(X_reason_test)
        
        print(classification_report(y_reason_test, y_reason_pred))
        print(f"Accuracy: {accuracy_score(y_reason_test, y_reason_pred):.4f}")
        
        return y_prob
    
    def prepare_input(self, input_data):
        """Prepare user input for prediction"""
        input_df = pd.DataFrame([input_data])
        
        # Convert time strings to datetime
        input_df['start_time'] = pd.to_datetime(input_df['start_time'])
        input_df['end_time'] = pd.to_datetime(input_df['end_time'])
        
        # Calculate duration
        input_df['duration_minutes'] = (
            input_df['end_time'] - input_df['start_time']
        ).dt.total_seconds() / 60
        
        # Extract time features
        input_df['start_hour'] = input_df['start_time'].dt.hour
        input_df['start_dayofweek'] = input_df['start_time'].dt.dayofweek
        input_df['start_month'] = input_df['start_time'].dt.month
        
        # Encode categorical variables
        for col in ['power_plant', 'area']:
            le = self.encoders.get(col)
            if le:
                try:
                    input_df[col + '_encoded'] = le.transform([input_df[col][0]])
                except ValueError:
                    # Handle unseen categories
                    input_df[col + '_encoded'] = len(le.classes_)
        
        return input_df
    
    def predict_failure(self, input_data):
        """Make prediction on user input"""
        # Prepare input
        input_df = self.prepare_input(input_data)
        
        # Ensure we have all required features
        if not all(col in input_df.columns for col in self.features):
            missing = set(self.features) - set(input_df.columns)
            raise ValueError(f"Missing features in input: {missing}")
        
        X_input = input_df[self.features]
        
        # Make failure prediction
        failure_prediction = self.model.predict(X_input)[0]
        failure_probability = self.model.predict_proba(X_input)[0][1]
        
        # Make reason prediction
        reason_prediction = self.reason_model.predict(X_input)[0]
        
        # Get the actual reason text from the encoder
        reason_encoder = self.encoders.get('reason', None)
        if reason_encoder:
            try:
                predicted_reason = reason_encoder.inverse_transform([reason_prediction])[0]
            except:
                predicted_reason = "unknown"
        else:
            predicted_reason = "unknown"
        
        # Determine if it's a grid failure based on predicted reason
        is_grid_failure = any(gfr in predicted_reason for gfr in self.grid_failure_reasons)
        
        # Prepare result
        result = {
            'grid_failure': 'Yes' if is_grid_failure else 'No',
            'predicted_reason': predicted_reason,
            'confidence': float(failure_probability * 100),
        }
        
        # Add preventive measures if failure
        if is_grid_failure:
            preventive_measures = []
            
            if 'animal' in predicted_reason:
                preventive_measures.append("Install animal guards around equipment")
            if 'overload' in predicted_reason:
                preventive_measures.extend([
                    "Upgrade infrastructure for peak loads",
                    "Implement load shedding strategies"
                ])
            if 'weather' in predicted_reason:
                preventive_measures.extend([
                    "Use weather-resistant equipment",
                    "Improve vegetation management near power lines"
                ])
            if 'equipment' in predicted_reason:
                preventive_measures.extend([
                    "Implement predictive maintenance",
                    "Replace aging equipment"
                ])
            
            result['preventive_measures'] = preventive_measures
        
        return result
    
    def save_model(self, filepath):
        """Save the trained models and encoders"""
        joblib.dump({
            'model': self.model,
            'reason_model': self.reason_model,
            'encoders': self.encoders,
            'features': self.features,
            'target': self.target,
            'reason_features': self.reason_features,
            'grid_failure_reasons': self.grid_failure_reasons
        }, filepath)
    
    def load_saved_model(self, filepath):
        """Load previously saved models"""
        saved_data = joblib.load(filepath)
        self.model = saved_data['model']
        self.reason_model = saved_data['reason_model']
        self.encoders = saved_data['encoders']
        self.features = saved_data['features']
        self.target = saved_data['target']
        self.reason_features = saved_data['reason_features']
        self.grid_failure_reasons = saved_data['grid_failure_reasons']

def get_user_input():
    """Collect user input for prediction"""
    print("\nPlease provide the following details for prediction:")
    
    input_data = {
        'power_plant': input("Power Plant Name: ").strip(),
        'start_time': input("Start Time (YYYY-MM-DD HH:MM:SS): ").strip(),
        'end_time': input("End Time (YYYY-MM-DD HH:MM:SS): ").strip(),
        'area': input("Geographical Area: ").strip()
    }
    
    return input_data

def main():
    predictor = PowerGridFailurePredictor()
    
    # Automatically load and process the data
    try:
        print("Loading data from power_outage.xlsx...")
        df = predictor.load_data("outage_data.xlsx")
        df = predictor.engineer_features(df)
        
        # Prepare data for failure prediction
        X = df[predictor.features]
        y = df[predictor.target]
        
        # Prepare data for reason prediction
        X_reason = df[predictor.reason_features]
        y_reason = df['reason_encoded']
        
        # Check class distribution
        print("\nClass distribution for grid failure:")
        print(y.value_counts())
        
        # Split data without stratification if necessary
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        X_reason_train, X_reason_test, y_reason_train, y_reason_test = train_test_split(
            X_reason, y_reason, test_size=0.2, random_state=42
        )
        
        print("Training models...")
        predictor.train_model(X_train, y_train, X_reason_train, y_reason_train)
        
        print("\nModel Evaluation:")
        predictor.evaluate_model(X_test, y_test, X_reason_test, y_reason_test)
        
        # Save the trained models
        predictor.save_model("grid_failure_model.pkl")
        print("\nModels saved as grid_failure_model.pkl")
        
    except Exception as e:
        print(f"Error during model training: {e}")
        return
    
    # Interactive prediction loop
    while True:
        try:
            input_data = get_user_input()
            result = predictor.predict_failure(input_data)
            
            print("\nPrediction Result:")
            print(f"Predicted Reason: {result['predicted_reason']}")
            print(f"Grid Failure: {result['grid_failure']}")
            print(f"Confidence: {result['confidence']:.2f}%")
            
            if result['grid_failure'] == 'Yes':
                print("\nSuggested Preventive Measures:")
                for measure in result.get('preventive_measures', []):
                    print(f"- {measure}")
            
        except Exception as e:
            print(f"\nError: {e}")
        
        continue_pred = input("\nMake another prediction? (yes/no): ").lower()
        if continue_pred != 'yes':
            break

if __name__ == "__main__":
    main()