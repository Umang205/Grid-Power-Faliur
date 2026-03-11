import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_ACTUAL_API_KEY_HERE')

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Emergency Contact Numbers
EMERGENCY_CONTACTS = [
    {'number': '9307014709', 'message': 'There may be a power outage in your area.'},
    {'number': '9161151800', 'message': 'There may be a power outage in your area. Please take preventive measures to avoid the outage.'},
    {'number': '9518192801', 'message': 'There may be a power outage in your area. Please take preventive measures to avoid the outage.'}
]
