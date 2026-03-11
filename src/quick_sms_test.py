import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Test phone number
TEST_NUMBER = '+919307014709'

def send_test_sms():
    print("Attempting to send SMS...")
    print(f"Twilio Account SID: {TWILIO_ACCOUNT_SID}")
    print(f"Twilio Phone Number: {TWILIO_PHONE_NUMBER}")

    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send test SMS
        message = client.messages.create(
            body="Test SMS from Power Grid Analysis System",
            from_=TWILIO_PHONE_NUMBER,
            to=TEST_NUMBER
        )
        
        print("SMS sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
    
    except Exception as e:
        print(f"Failed to send SMS: {e}")

if __name__ == '__main__':
    send_test_sms()
