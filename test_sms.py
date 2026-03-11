import os
import sys
import traceback
from dotenv import load_dotenv
from twilio.rest import Client
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('sms_test.log'),
                        logging.StreamHandler(sys.stdout)
                    ])

# Load environment variables
load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Emergency contact numbers
EMERGENCY_CONTACTS = [
    {'number': '9307014709', 'message': 'Test: There may be a power outage in your area.'},
    {'number': '9161151800', 'message': 'Test: There may be a power outage in your area. Please take preventive measures to avoid the outage.'},
    {'number': '9518192801', 'message': 'Test: There may be a power outage in your area. Please take preventive measures to avoid the outage.'}
]

def send_test_sms():
    print("=" * 50)
    print("Environment Variables:")
    print(f"TWILIO_ACCOUNT_SID: {TWILIO_ACCOUNT_SID}")
    print(f"TWILIO_AUTH_TOKEN: {'*' * len(TWILIO_AUTH_TOKEN) if TWILIO_AUTH_TOKEN else 'MISSING'}")
    print(f"TWILIO_PHONE_NUMBER: {TWILIO_PHONE_NUMBER}")
    print("=" * 50)

    # Validate credentials
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logging.error("Missing Twilio credentials!")
        print("Error: Missing Twilio credentials!")
        return

    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send SMS to each emergency contact
        for contact in EMERGENCY_CONTACTS:
            try:
                message = client.messages.create(
                    body=contact['message'],
                    from_=TWILIO_PHONE_NUMBER,
                    to=f'+91{contact["number"]}'  # Assuming Indian phone numbers
                )
                print(f"SMS sent to {contact['number']} successfully!")
                print(f"Message SID: {message.sid}")
                print(f"Status: {message.status}")
            except Exception as e:
                print(f"Failed to send SMS to {contact['number']}")
                print(f"Error details: {str(e)}")
                traceback.print_exc()
    
    except Exception as e:
        print("Twilio SMS setup failed:")
        print(f"Error: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    print("Starting SMS Test...")
    send_test_sms()
