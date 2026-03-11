import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import joblib
import os

# Create models directory
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# Create sample data
print("Creating sample data...")
np.random.seed(42)
n_samples = 1000

# Generate dates
base_date = datetime(2023, 1, 1)
start_times = [base_date + timedelta(hours=x) for x in range(n_samples)]
durations = np.random.randint(1, 24, n_samples)
end_times = [start + timedelta(hours=dur) for start, dur in zip(start_times, durations)]

# Create sample data
areas = ['North Region', 'South Region', 'East Region', 'West Region']
power_plants = ['Plant A', 'Plant B', 'Plant C', 'Plant D']
reasons = ['Equipment failure', 'Maintenance', 'Weather rainstorm', 'Overload', 'Animal intervention']

data = {
    'start_time': start_times,
    'end_time': end_times,
    'area': np.random.choice(areas, n_samples),
    'power_plant': np.random.choice(power_plants, n_samples),
    'reason': np.random.choice(reasons, n_samples)
}

# Create DataFrame
df = pd.DataFrame(data)
print("Sample data created successfully!")

# Preprocess data
print("Preprocessing data...")

# Create encoders
encoders = {}
for column in ['area', 'power_plant', 'reason']:
    encoder = LabelEncoder()
    df[f'{column}_encoded'] = encoder.fit_transform(df[column])
    encoders[column] = encoder

# Extract features
df['duration_hours'] = (pd.to_datetime(df['end_time']) - pd.to_datetime(df['start_time'])).dt.total_seconds() / 3600
df['hour_of_day'] = pd.to_datetime(df['start_time']).dt.hour
df['day_of_week'] = pd.to_datetime(df['start_time']).dt.dayofweek
df['month'] = pd.to_datetime(df['start_time']).dt.month
df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
df['year'] = pd.to_datetime(df['start_time']).dt.year
df['quarter'] = pd.to_datetime(df['start_time']).dt.quarter

# Prepare features
features = [
    'duration_hours', 'hour_of_day', 'day_of_week', 'month',
    'is_weekend', 'year', 'quarter', 'area_encoded', 'power_plant_encoded'
]

X = df[features].values
y = df['reason_encoded'].values

# Initialize and fit imputer
print("Fitting imputer...")
imputer = SimpleImputer(strategy='median')
X = imputer.fit_transform(X)

# Initialize and fit scaler
print("Fitting scaler...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Random Forest
print("Training Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

# Save all artifacts
print("Saving model artifacts...")
joblib.dump(model, os.path.join(MODEL_DIR, 'grid_failure_rf_model.joblib'))
joblib.dump(scaler, os.path.join(MODEL_DIR, 'rf_scaler.joblib'))
joblib.dump(encoders, os.path.join(MODEL_DIR, 'rf_encoders.joblib'))
joblib.dump(imputer, os.path.join(MODEL_DIR, 'rf_imputer.joblib'))

print("All model artifacts saved successfully!")
print(f"Model files saved in: {MODEL_DIR}") 