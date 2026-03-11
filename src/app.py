from flask import Flask, render_template, request, jsonify, send_from_directory
from geocoding import location_geocoder
from flask_socketio import SocketIO, emit
import os
import sys
import logging
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import random
import time
import openpyxl
from twilio.rest import Client

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from config import (
        TWILIO_ACCOUNT_SID, 
        TWILIO_AUTH_TOKEN, 
        TWILIO_PHONE_NUMBER, 
        EMERGENCY_CONTACTS
    )
except ImportError:
    # Fallback configuration if import fails
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    EMERGENCY_CONTACTS = [
        {'number': 'message': 'There may be a power outage in your area.'},
        {'number':  'message': 'There may be a power outage in your area. Please take preventive measures to avoid the outage.'},
        {'number': ' message': 'There may be a power outage in your area. Please take preventive measures to avoid the outage.'}
    ]

# Get the absolute path to the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app with proper template and static paths
app = Flask(__name__,
            static_folder=os.path.join(PROJECT_DIR, 'static'),
            template_folder=os.path.join(PROJECT_DIR, 'templates'))
socketio = SocketIO(app)

# Define model paths
MODEL_DIR = os.path.join(PROJECT_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'grid_failure_rf_model.joblib')
SCALER_PATH = os.path.join(MODEL_DIR, 'rf_scaler.joblib')
ENCODERS_PATH = os.path.join(MODEL_DIR, 'rf_encoders.joblib')
IMPUTER_PATH = os.path.join(MODEL_DIR, 'rf_imputer.joblib')

class SafeLabelEncoder:
    def __init__(self, encoder):
        self.encoder = encoder
        self.classes_ = encoder.classes_
        
    def transform(self, values):
        # Handle unknown values
        encoded = np.zeros(len(values), dtype=int)
        for idx, val in enumerate(values):
            try:
                encoded[idx] = self.encoder.transform([val])[0]
            except:
                # Assign the last index for unknown values
                encoded[idx] = len(self.classes_) - 1
        return encoded

def load_models():
    """Load all required model artifacts."""
    try:
        if not os.path.exists(MODEL_DIR):
            raise FileNotFoundError(f"Models directory not found at: {MODEL_DIR}")
        
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        encoders = joblib.load(ENCODERS_PATH)
        imputer = joblib.load(IMPUTER_PATH)
        feature_names = joblib.load(os.path.join(MODEL_DIR, 'feature_names.joblib'))
        
        # Wrap encoders with SafeLabelEncoder
        safe_encoders = {}
        for key, encoder in encoders.items():
            safe_encoders[key] = SafeLabelEncoder(encoder)
        
        return model, scaler, safe_encoders, imputer, feature_names
    except Exception as e:
        print(f"Error loading models: {str(e)}")
        return None, None, None, None, None

# Load models
model, scaler, encoders, imputer, feature_names = load_models()

def prepare_input_data(input_data):
    """Prepare input data for prediction."""
    try:
        # Convert timestamps to datetime
        start_time = pd.to_datetime(input_data['start_time'])
        end_time = pd.to_datetime(input_data['end_time'])
        
        # Create location feature
        location = f"{input_data['area']}_{input_data['power_plant']}"
        
        # Extract all features in the same order as training
        features = {
            'duration_hours': (end_time - start_time).total_seconds() / 3600,
            'hour_of_day': start_time.hour,
            'day_of_week': start_time.dayofweek,
            'month': start_time.month,
            'year': start_time.year,
            'quarter': (start_time.month - 1) // 3 + 1,
            'is_weekend': 1 if start_time.dayofweek >= 5 else 0,
            'is_holiday': 1 if start_time.dayofweek >= 5 else 0,  # Simplified holiday detection
            'is_peak_hour': 1 if 9 <= start_time.hour <= 20 else 0,
            'season': 1 if start_time.month in [12,1,2] else 2 if start_time.month in [3,4,5] else 3 if start_time.month in [6,7,8] else 4,
            'is_long_duration': 1 if (end_time - start_time).total_seconds() / 3600 > 12 else 0,  # Using 12 hours as threshold
            'area_encoded': encoders['area'].transform([input_data['area']])[0],
            'power_plant_encoded': encoders['power_plant'].transform([input_data['power_plant']])[0],
            'location_encoded': encoders['location'].transform([location])[0],
            'latitude': input_data.get('latitude', 28.6139),  # Default to Delhi center
            'longitude': input_data.get('longitude', 77.2090)  # Default to Delhi center
        }
        
        # Create feature vector in the same order as training
        feature_order = [
            'duration_hours',
            'hour_of_day',
            'day_of_week',
            'month',
            'year',
            'quarter',
            'is_weekend',
            'is_holiday',
            'is_peak_hour',
            'season',
            'is_long_duration',
            'area_encoded',
            'power_plant_encoded',
            'location_encoded',
            'latitude',
            'longitude'
        ]
        
        X = np.array([[features[f] for f in feature_order]])
        return X
    except Exception as e:
        raise ValueError(f"Error preparing input data: {str(e)}")

def make_prediction(X):
    """Make prediction with error handling."""
    try:
        # Apply imputer
        X_imputed = imputer.transform(X)
        
        # Apply scaler
        X_scaled = scaler.transform(X_imputed)
        
        # Make prediction
        pred_proba = model.predict_proba(X_scaled)[0]
        predicted_class = model.predict(X_scaled)[0]
        
        # Get the predicted reason
        reason = encoders['reason'].classes_[predicted_class]
        confidence = float(max(pred_proba))
        
        # Determine if it's a grid failure
        failure_reasons = ['equipment failure', 'weather rainstorm', 'overload', 'animal intervention']
        is_grid_failure = any(fr in reason.lower() for fr in failure_reasons)
        
        # Recommended Action
        recommended_action = "No immediate action required."
        if confidence >= 0.75:
            recommended_action = "High risk detected. Immediate maintenance and grid stabilization required."
        elif confidence >= 0.5:
            recommended_action = "Moderate risk. Conduct thorough system inspection and prepare contingency plans."
        elif confidence >= 0.3:
            recommended_action = "Low risk. Monitor system closely and perform preventive maintenance."
        
        return {
            'status': 'success',
            'is_grid_failure': bool(is_grid_failure),
            'reason': reason,
            'confidence': confidence,
            'recommended_action': recommended_action
        }
    except Exception as e:
        raise ValueError(f"Error making prediction: {str(e)}")

def send_emergency_sms(confidence):
    """Send SMS alerts if grid failure confidence is above 60%."""
    # Convert percentage to decimal if needed
    if confidence > 1:
        confidence = confidence / 100.0
    
    if confidence > 0.6:
        try:
            # Initialize Twilio client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            # Send SMS to each emergency contact
            for contact in EMERGENCY_CONTACTS:
                try:
                    message = client.messages.create(
                        body=f"EMERGENCY ALERT: Grid failure risk is {confidence*100:.2f}%",
                        from_=TWILIO_PHONE_NUMBER,
                        to=f'+91{contact["number"]}'  # Assuming Indian phone numbers
                    )
                    logging.info(f"SMS sent to {contact['number']}: {message.sid}")
                except Exception as e:
                    logging.error(f"Failed to send SMS to {contact['number']}: {str(e)}")
        
        except Exception as e:
            logging.error(f"Twilio SMS setup failed: {str(e)}")

# Simulated grid data
grid_data = {
    'north': {'loadPercentage': 0, 'averageLoad': 0, 'peakLoad': 0},
    'south': {'loadPercentage': 0, 'averageLoad': 0, 'peakLoad': 0},
    'east': {'loadPercentage': 0, 'averageLoad': 0, 'peakLoad': 0},
    'west': {'loadPercentage': 0, 'averageLoad': 0, 'peakLoad': 0}
}

# Generate random data for testing
def generate_random_data():
    for region in grid_data:
        load = random.uniform(0, 100)
        grid_data[region]['loadPercentage'] = load
        grid_data[region]['averageLoad'] = random.uniform(0, 100)
        grid_data[region]['peakLoad'] = random.uniform(0, 100)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/report_issue')
def report_issue():
    return render_template('report_issue.html')

@app.route('/plot_gallery')
def plot_gallery():
    """
    Serve a gallery of plots from the Plot directory
    """
    # Determine the absolute path to the Plot directory
    plot_dir = os.path.join(PROJECT_DIR, '..', 'Plot')
    
    # Ensure the directory exists
    if not os.path.exists(plot_dir):
        return "Plot directory not found", 404
    
    # Get list of image files
    plot_files = [f for f in os.listdir(plot_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    return render_template('plot_gallery.html', plot_files=plot_files)

@app.route('/plot/<filename>')
def serve_plot(filename):
    """
    Serve individual plot images
    """
    plot_dir = os.path.join(PROJECT_DIR, '..', 'Plot')
    return send_from_directory(plot_dir, filename)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('data_update', get_grid_status())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('region_selection')
def handle_region_selection(data):
    print(f'Region selected: {data["region"]}')
    emit('data_update', get_grid_status())

@socketio.on('time_range')
def handle_time_range(data):
    print(f'Time range changed: {data["range"]}')
    emit('data_update', get_grid_status())

def get_grid_status():
    generate_random_data()
    return {
        'timestamp': time.time(),
        'regions': grid_data,
        'overallLoad': sum(region['loadPercentage'] for region in grid_data.values()) / len(grid_data),
        'stressLevel': sum(region['loadPercentage'] for region in grid_data.values()) / len(grid_data)
    }

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if not all([model, scaler, encoders, imputer]):
            raise ValueError("Model artifacts not properly loaded")
        
        # Get input data
        input_data = request.get_json()
        
        # Validate input data
        required_fields = ['start_time', 'end_time', 'area', 'power_plant']
        for field in required_fields:
            if field not in input_data or not input_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Geocode the location
        location_info = location_geocoder.geocode_location(input_data['area'])
        
        # Add geocoding information to input data
        input_data['latitude'] = location_info['latitude']
        input_data['longitude'] = location_info['longitude']
        
        # Prepare input data
        X = prepare_input_data(input_data)
        
        # Make prediction
        prediction = make_prediction(X)
        
        # Combine prediction with location info
        prediction.update({
            'location_details': location_info
        })
        
        # Send SMS if confidence is high
        send_emergency_sms(prediction['confidence'])
        
        return jsonify(prediction)
    
    except ValueError as ve:
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Unexpected error: {str(e)}"
        }), 500

@app.route('/submit_issue', methods=['POST'])
def submit_issue():
    try:
        # Comprehensive logging setup
        import logging
        import traceback
        import os
        import openpyxl
        from datetime import datetime
        
        # Configure logging
        log_path = os.path.join(PROJECT_DIR, 'issue_report.log')
        logging.basicConfig(
            filename=log_path, 
            level=logging.DEBUG, 
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Log the full request details
        logging.debug(f"Received form data: {dict(request.form)}")
        
        # Extract form data
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        area = request.form.get('area', '').strip()
        power_plant = request.form.get('power_plant', '').strip()
        reason = request.form.get('reason', '').strip()
        
        # Validate input
        if not all([start_time, end_time, area, power_plant, reason]):
            missing_fields = [
                field for field, value in {
                    'Start Time': start_time,
                    'End Time': end_time,
                    'Area': area,
                    'Power Plant': power_plant,
                    'Reason': reason
                }.items() if not value
            ]
            error_message = f"Missing required fields: {', '.join(missing_fields)}"
            logging.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 400
        
        # Determine exact Excel file path
        try:
            data_dir = os.path.join(PROJECT_DIR, 'data')
            os.makedirs(data_dir, exist_ok=True)
        except Exception as dir_error:
            logging.error(f"Failed to create data directory: {str(dir_error)}")
            return jsonify({
                'status': 'error',
                'message': f'Cannot create data directory: {str(dir_error)}'
            }), 500
        
        excel_path = os.path.join(data_dir, 'real_time_data.xlsx')
        
        logging.debug(f"Excel file will be saved at: {excel_path}")
        
        try:
            # Open or create workbook
            if os.path.exists(excel_path):
                wb = openpyxl.load_workbook(excel_path)
                ws = wb.active
            else:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = 'Power Grid Issues'
                headers = [
                    'Timestamp', 'Start Time', 'End Time', 'Area', 
                    'Power Plant', 'Reason for Failure'
                ]
                ws.append(headers)
            
            # Prepare row data
            row_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                start_time,
                end_time,
                area,
                power_plant,
                reason
            ]
            
            logging.debug(f"Row data to be appended: {row_data}")
            
            # Append row
            ws.append(row_data)
            
            # Save workbook with explicit error handling
            try:
                wb.save(excel_path)
                logging.info(f"Data successfully saved to {excel_path}")
                
                return jsonify({
                    'status': 'success',
                    'message': 'Issue reported successfully',
                    'file_path': excel_path
                }), 200
            
            except PermissionError:
                logging.error(f"Permission denied when saving to {excel_path}")
                return jsonify({
                    'status': 'error',
                    'message': f'Permission denied. Cannot save to {excel_path}'
                }), 500
            
            except Exception as save_error:
                logging.error(f"Excel save error: {str(save_error)}")
                logging.error(traceback.format_exc())
                return jsonify({
                    'status': 'error',
                    'message': f'Error saving Excel file: {str(save_error)}'
                }), 500
        
        except Exception as file_error:
            logging.error(f"Excel file processing error: {str(file_error)}")
            logging.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': f'Error processing Excel file: {str(file_error)}'
            }), 500
    
    except Exception as unexpected_error:
        logging.error(f"Unexpected error: {str(unexpected_error)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Unexpected server error: {str(unexpected_error)}'
        }), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)