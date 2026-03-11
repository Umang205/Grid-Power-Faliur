import os
import sys
import logging
from twilio.rest import Client
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('alert_test.log'),
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
    {'number': '9307014709', 'message': 'Test: High grid failure risk detected.'},
    {'number': '9161151800', 'message': 'Test: Critical grid failure probability.'},
    {'number': '9518192801', 'message': 'Test: Immediate preventive action required.'}
]

def test_twilio_connection():
    """Test Twilio connection and SMS sending"""
    print("=" * 50)
    print("Twilio Connection Test")
    print("=" * 50)
    
    # Validate credentials
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logging.error("Missing Twilio credentials!")
        print("Error: Missing Twilio credentials!")
        return False
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send test SMS to each emergency contact
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
                logging.info(f"Test SMS sent to {contact['number']}: {message.sid}")
            except Exception as e:
                print(f"Failed to send SMS to {contact['number']}")
                print(f"Error details: {str(e)}")
                logging.error(f"Test SMS failed for {contact['number']}: {str(e)}")
        
        return True
    
    except Exception as e:
        print("Twilio SMS setup failed:")
        print(f"Error: {str(e)}")
        logging.error(f"Twilio connection test failed: {str(e)}")
        return False

def main():
    print("Starting Twilio SMS Alert System Test...")
    
    # Test Twilio connection and SMS sending
    test_result = test_twilio_connection()
    
    if test_result:
        print("\n✅ Twilio SMS Alert System Test PASSED")
        sys.exit(0)
    else:
        print("\n❌ Twilio SMS Alert System Test FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main()
