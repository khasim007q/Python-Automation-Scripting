import pandas as pd
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import os
from typing import List, Dict

class EventAutomation:
    def __init__(self, csv_file_path):
        """Initialize automation with cleaned CSV data and messages"""
        self.df = pd.read_csv(csv_file_path)
        self.load_messages()
        
    def load_messages(self):
        """Load generated messages from CSV"""
        try:
            messages_df = pd.read_csv('personalized_messages.csv')
            self.messages = messages_df.to_dict('records')
            print(f"✅ Loaded {len(self.messages)} messages from personalized_messages.csv")
        except FileNotFoundError:
            print("❌ personalized_messages.csv not found. Please run personalized_messaging.py first!")
            self.messages = []

class EmailAutomation(EventAutomation):
    def __init__(self, csv_file_path):
        super().__init__(csv_file_path)
        self.smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True
        }
    
    def setup_gmail_credentials(self):
        """
        Setup Gmail credentials
        Note: For production use, you'll need:
        1. App Password from Google Account settings
        2. Environment variables for security
        """
        return {
            'email': os.getenv('GMAIL_EMAIL', ''),
            'password': os.getenv('GMAIL_APP_PASSWORD', '')
        }
    
    def validate_email_setup(self, email, password):
        """Test SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            if self.smtp_config['use_tls']:
                server.starttls()
            server.login(email, password)
            server.quit()
            return True
        except Exception as e:
            print(f"❌ Email setup validation failed: {e}")
            return False
    
    def send_batch_emails(self, sender_email=None, sender_password=None, 
                         batch_size=10, delay_seconds=2, dry_run=True):
        """
        Send emails in batches with rate limiting
        """
        if not self.messages:
            print("❌ No messages to send!")
            return False
        
        credentials = self.setup_gmail_credentials()
        sender_email = sender_email or credentials['email']
        sender_password = sender_password or credentials['password']
        
        if dry_run:
            print("🧪 DRY RUN MODE - Simulating email sending")
            print(f"📧 Would send {len(self.messages)} emails in batches of {batch_size}")
            print(f"⏱️  With {delay_seconds}s delay between emails")
            
            for i, msg in enumerate(self.messages):
                print(f"[{i+1}/{len(self.messages)}] Would send to: {msg['email']}")
                if (i + 1) % batch_size == 0:
                    print(f"   💤 Would pause for {delay_seconds} seconds...")
            
            return True
        
        if not sender_email or not sender_password:
            print("❌ Email credentials required. Set GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables.")
            return False
        
        if not self.validate_email_setup(sender_email, sender_password):
            return False
        
        print(f"📧 Starting batch email sending...")
        successful_sends = 0
        failed_sends = 0
        
        try:
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            if self.smtp_config['use_tls']:
                server.starttls()
            server.login(sender_email, sender_password)
            
            for i, msg in enumerate(self.messages):
                try:
                    # Create email
                    email_msg = MIMEMultipart()
                    email_msg['From'] = sender_email
                    email_msg['To'] = msg['email']
                    email_msg['Subject'] = "Follow-up from our recent event 🎉"
                    
                    # Add HTML formatting for better presentation
                    html_message = f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                                <h2 style="color: #2c3e50;">Thanks for your interest in our event!</h2>
                                <p>{msg['message']}</p>
                                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                                <p style="font-size: 12px; color: #666;">
                                    This is an automated message. If you have any questions, please reply to this email.
                                </p>
                            </div>
                        </body>
                    </html>
                    """
                    
                    email_msg.attach(MIMEText(html_message, 'html'))
                    
                    # Send email
                    server.sendmail(sender_email, msg['email'], email_msg.as_string())
                    successful_sends += 1
                    print(f"✅ [{i+1}/{len(self.messages)}] Sent to {msg['email']}")
                    
                    # Rate limiting
                    if (i + 1) % batch_size == 0 and i + 1 < len(self.messages):
                        print(f"   💤 Pausing for {delay_seconds} seconds...")
                        time.sleep(delay_seconds)
                    
                except Exception as e:
                    failed_sends += 1
                    print(f"❌ [{i+1}/{len(self.messages)}] Failed to send to {msg['email']}: {e}")
            
            server.quit()
            
        except Exception as e:
            print(f"❌ SMTP Server Error: {e}")
            return False
        
        print(f"\n📊 Email Sending Summary:")
        print(f"   ✅ Successful: {successful_sends}")
        print(f"   ❌ Failed: {failed_sends}")
        print(f"   📈 Success Rate: {(successful_sends/len(self.messages)*100):.1f}%")
        
        return successful_sends > 0

class TelegramAutomation(EventAutomation):
    def __init__(self, csv_file_path, bot_token=None):
        super().__init__(csv_file_path)
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def validate_bot_token(self):
        """Validate Telegram bot token"""
        if not self.bot_token:
            return False
        
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def create_message_queue(self, output_file='telegram_queue.json'):
        """Create a Telegram message queue with priority and scheduling"""
        if not self.messages:
            print("❌ No messages to queue!")
            return False
        
        queue = {
            "bot_info": {
                "token": "YOUR_BOT_TOKEN_HERE",
                "name": "EventFollowUpBot"
            },
            "queue_metadata": {
                "created_at": datetime.now().isoformat(),
                "total_messages": len(self.messages),
                "estimated_send_time": f"{len(self.messages) * 2} seconds"
            },
            "messages": []
        }
        
        # Add messages with priority and scheduling
        for i, msg in enumerate(self.messages):
            # Determine priority based on user engagement
            user_data = self.df[self.df['email'] == msg['email']].iloc[0]
            
            if user_data['has_joined_event']:
                priority = "high"
                delay_minutes = 0  # Send immediately
            else:
                priority = "normal" 
                delay_minutes = 30  # Send after 30 minutes
            
            queue_item = {
                "id": f"msg_{i+1:03d}",
                "recipient_email": msg['email'],
                "message_text": msg['message'],
                "priority": priority,
                "scheduled_delay_minutes": delay_minutes,
                "tags": ["event_followup", "automated"],
                "retry_count": 0,
                "max_retries": 3,
                "status": "pending"
            }
            
            queue["messages"].append(queue_item)
        
        # Save queue to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
        
        print(f"📱 Telegram message queue created: {output_file}")
        print(f"   📊 High priority messages: {sum(1 for m in queue['messages'] if m['priority'] == 'high')}")
        print(f"   📊 Normal priority messages: {sum(1 for m in queue['messages'] if m['priority'] == 'normal')}")
        
        return output_file
    
    def simulate_telegram_sending(self):
        """Simulate sending messages via Telegram bot"""
        if not self.messages:
            print("❌ No messages to send!")
            return False
        
        print("🤖 Simulating Telegram Bot Message Sending")
        print("="*50)
        
        # Group by priority
        high_priority = [msg for msg in self.messages if self.df[self.df['email'] == msg['email']]['has_joined_event'].iloc[0]]
        normal_priority = [msg for msg in self.messages if not self.df[self.df['email'] == msg['email']]['has_joined_event'].iloc[0]]
        
        print(f"📊 Queue Statistics:")
        print(f"   🔥 High Priority (joined event): {len(high_priority)}")
        print(f"   📋 Normal Priority (didn't join): {len(normal_priority)}")
        
        print(f"\n🚀 Sending High Priority Messages...")
        for i, msg in enumerate(high_priority):
            print(f"   [{i+1}/{len(high_priority)}] 📤 To: {msg['email'][:20]}...")
            print(f"       💬 Message: {msg['message'][:50]}...")
            time.sleep(0.5)  # Simulate API call delay
        
        print(f"\n📤 Sending Normal Priority Messages...")
        for i, msg in enumerate(normal_priority):
            print(f"   [{i+1}/{len(normal_priority)}] 📤 To: {msg['email'][:20]}...")
            print(f"       💬 Message: {msg['message'][:50]}...")
            time.sleep(0.5)  # Simulate API call delay
        
        print(f"\n✅ Simulation Complete!")
        print(f"   📊 Total messages processed: {len(self.messages)}")
        
        return True

def main():
    """Main automation script"""
    print("🤖 Event Follow-up Automation System")
    print("="*50)
    
    # Check if required files exist
    if not os.path.exists('cleaned_output.csv'):
        print("❌ cleaned_output.csv not found!")
        return
    
    if not os.path.exists('personalized_messages.csv'):
        print("❌ personalized_messages.csv not found!")
        print("   Please run personalized_messaging.py first!")
        return
    
    print("1️⃣  Email Automation Demo")
    print("-" * 30)
    email_automation = EmailAutomation('cleaned_output.csv')
    
    # Demo email sending (dry run)
    email_automation.send_batch_emails(
        batch_size=5,
        delay_seconds=1,
        dry_run=True
    )
    
    print(f"\n2️⃣  Telegram Bot Automation Demo")
    print("-" * 30)
    telegram_automation = TelegramAutomation('cleaned_output.csv')
    
    # Create message queue
    telegram_automation.create_message_queue()
    
    # Simulate sending
    telegram_automation.simulate_telegram_sending()
    
    print(f"\n✨ Automation Demo Complete!")
    print(f"\n📋 To use in production:")
    print(f"   📧 Email: Set GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables")
    print(f"   🤖 Telegram: Set TELEGRAM_BOT_TOKEN environment variable")
    print(f"   🚀 Change dry_run=False for actual sending")

if __name__ == "__main__":
    main()