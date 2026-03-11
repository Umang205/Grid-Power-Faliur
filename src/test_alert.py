import requests
import json

# Test URL for prediction
url = 'http://localhost:5000/predict'

# Sample input data
input_data = {
    'start_time': '2025-04-16 14:00:00',
    'end_time': '2025-04-16 15:00:00',
    'area': 'North',
    'power_plant': 'Solar',
    # Simulate high-risk scenario
    'load_percentage': 95,
    'temperature': 45,
    'maintenance_status': 'critical'
}

# Send prediction request
try:
    response = requests.post(url, 
                             json=input_data, 
                             headers={'Content-Type': 'application/json'})
    
    # Print the response
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json())

except requests.exceptions.RequestException as e:
    print("Error occurred:", e)
