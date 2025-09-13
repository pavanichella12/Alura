import os
from typing import Dict, Optional
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NotificationSystem:
    def __init__(self):
        # You can set these environment variables for WhatsApp integration
        self.whatsapp_api_key = os.getenv('WHATSAPP_API_KEY')
        self.reviewer_phone = os.getenv('REVIEWER_PHONE')
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE')
    
    def send_whatsapp_notification(self, challenge_data: Dict) -> bool:
        """Send WhatsApp notification to reviewer about new challenge"""
        try:
            # Check if Twilio credentials are available and not placeholder values
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone, self.reviewer_phone]):
                print("WhatsApp notification not configured. Set environment variables.")
                return False
            
            # Check if credentials are still placeholder values
            if (self.twilio_account_sid == "your_twilio_account_sid" or 
                self.twilio_auth_token == "your_twilio_auth_token" or
                self.twilio_phone == "your_twilio_phone_number" or
                self.reviewer_phone == "your_reviewer_phone_number"):
                print("WhatsApp notification not properly configured. Using fallback.")
                return False
            
            # Create message content
            message = self._create_challenge_message(challenge_data)
            
            # Send via Twilio WhatsApp API
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            
            data = {
                'From': f'whatsapp:{self.twilio_phone}',
                'To': f'whatsapp:{self.reviewer_phone}',
                'Body': message
            }
            
            response = requests.post(
                url,
                data=data,
                auth=(self.twilio_account_sid, self.twilio_auth_token)
            )
            
            if response.status_code == 201:
                print("WhatsApp notification sent successfully!")
                return True
            else:
                print(f"Failed to send WhatsApp notification: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending WhatsApp notification: {e}")
            return False
    
    def _create_challenge_message(self, challenge_data: Dict) -> str:
        """Create formatted message for WhatsApp notification"""
        message = f"""
🚨 NEW CHALLENGE SUBMITTED

User ID: {challenge_data['user_id'][:8]}...
Original Message: "{challenge_data['original_message']}"
Flagged Words: {', '.join(challenge_data['flagged_words'])}
Categories: {', '.join(challenge_data['categories'])}

User's Reason: "{challenge_data['challenge_reason']}"

Submitted: {challenge_data['created_at']}

Review this challenge in the admin panel.
        """
        return message.strip()
    
    def send_challenge_notification(self, challenge_data: Dict) -> bool:
        """Main method to send challenge notification"""
        # Try WhatsApp first
        whatsapp_sent = self.send_whatsapp_notification(challenge_data)
        
        if whatsapp_sent:
            return True
        else:
            # Fallback: Print to console and save to file
            return self.send_fallback_notification(challenge_data)
    
    def send_fallback_notification(self, challenge_data: Dict) -> bool:
        """Send notification via console and file when WhatsApp is not configured"""
        try:
            # Create notification message
            message = self._create_challenge_message(challenge_data)
            
            # Print to console
            print("\n" + "="*50)
            print("🚨 CHALLENGE NOTIFICATION (WhatsApp not configured)")
            print("="*50)
            print(message)
            print("="*50)
            
            # Save to file for manual review
            with open("pending_challenges.txt", "a") as f:
                f.write(f"\n{challenge_data['created_at']} - {message}\n")
            
            print("Challenge saved to 'pending_challenges.txt' for manual review")
            return True
            
        except Exception as e:
            print(f"Error sending fallback notification: {e}")
            return False
    
    def send_review_notification(self, challenge_id: int, status: str, reviewer_notes: str = None) -> bool:
        """Send notification to user about challenge review result"""
        try:
            # Get challenge details from database
            from ..core.database import ContentModerationDB
            db = ContentModerationDB()
            
            # Get challenge details
            challenges = db.get_pending_challenges()
            challenge = None
            for c in challenges:
                if c['challenge_id'] == challenge_id:
                    challenge = c
                    break
            
            if not challenge:
                return False
            
            # Create notification message
            if status == "approved":
                message = f"""
✅ CHALLENGE APPROVED

Your challenge for message: "{challenge['original_message']}"

Status: APPROVED ✅
Reviewer Notes: {reviewer_notes or 'No additional notes'}

Your message will now be delivered!
                """
            else:
                message = f"""
❌ CHALLENGE REJECTED

Your challenge for message: "{challenge['original_message']}"

Status: REJECTED ❌
Reviewer Notes: {reviewer_notes or 'No additional notes'}

Your message remains blocked.
                """
            
            # Send WhatsApp notification to user
            user_notification_data = {
                'user_id': challenge['user_id'],
                'original_message': challenge['original_message'],
                'status': status,
                'reviewer_notes': reviewer_notes,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return self.send_whatsapp_notification(user_notification_data)
            
        except Exception as e:
            print(f"Error sending review notification: {e}")
            return False 