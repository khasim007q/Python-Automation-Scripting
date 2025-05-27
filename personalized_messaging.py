import pandas as pd
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class PersonalizedMessenger:
    def __init__(self, csv_file_path):
        """Initialize the messenger with cleaned CSV data"""
        self.df = pd.read_csv(csv_file_path)
        self.messages = []
        
    def generate_personalized_message(self, row):
        """Generate a personalized message based on user data"""
        name = row['name'].split()[0] if row['name'] else "there"
        job_title = row['Job Title'] if pd.notna(row['Job Title']) and row['Job Title'].strip() else None
        has_joined = row['has_joined_event']
        has_linkedin = not row['linkedin_flag']  # linkedin_flag True means missing/incomplete
        
        # Base message templates
        if has_joined:
            # They joined the event
            if job_title and job_title.lower() != 'unemployed':
                message = f"🎉 Hey {name}, thanks for joining our session! As a {job_title.lower()}, we think you'll love our upcoming AI workflow tools. Want early access?"
            else:
                message = f"🎉 Hey {name}, thanks for joining our session! We're excited to have had you participate and would love to keep you updated on our upcoming events and tools!"
        else:
            # They didn't join the event
            if job_title and job_title.lower() != 'unemployed':
                message = f"Hi {name}, sorry we missed you at the last event! We're preparing another session that might better suit your interests as a {job_title}. Hope to see you next time!"
            else:
                message = f"Hi {name}, sorry we missed you at the last event! We're preparing another session with exciting content that we think you'll find valuable. Hope to see you next time!"
        
        # Add LinkedIn-specific messaging
        if not has_linkedin:
            message += " P.S. We'd love to connect with you on LinkedIn to keep you updated on future opportunities!"
            
        return message
    
    def generate_all_messages(self):
        """Generate personalized messages for all users"""
        self.messages = []
        
        for index, row in self.df.iterrows():
            message = self.generate_personalized_message(row)
            self.messages.append({
                'email': row['email'],
                'name': row['name'],
                'message': message,
                'has_joined_event': row['has_joined_event'],
                'job_title': row['Job Title']
            })
        
        return self.messages
    
    def save_messages_csv(self, output_file='personalized_messages.csv'):
        """Save messages to CSV file"""
        if not self.messages:
            self.generate_all_messages()
            
        # Create DataFrame with required columns
        messages_df = pd.DataFrame([
            {'email': msg['email'], 'message': msg['message']} 
            for msg in self.messages
        ])
        
        messages_df.to_csv(output_file, index=False)
        print(f"Messages saved to {output_file}")
        return output_file
    
    def save_messages_json(self, output_file='personalized_messages.json'):
        """Save messages to JSON file (bonus format)"""
        if not self.messages:
            self.generate_all_messages()
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, indent=2, ensure_ascii=False)
        
        print(f"Messages saved to {output_file}")
        return output_file
    
    def save_messages_txt(self, output_file='personalized_messages.txt'):
        """Save messages to TXT file (bonus format)"""
        if not self.messages:
            self.generate_all_messages()
            
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Personalized Messages Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for i, msg in enumerate(self.messages, 1):
                f.write(f"Message {i}:\n")
                f.write(f"To: {msg['email']} ({msg['name']})\n")
                f.write(f"Message: {msg['message']}\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"Messages saved to {output_file}")
        return output_file
    
    def send_email_smtp(self, smtp_server='smtp.gmail.com', smtp_port=587, 
                       sender_email=None, sender_password=None, test_mode=True):
        """
        Send emails using SMTP (Gmail setup)
        Note: In test_mode, it will only print what would be sent
        """
        if not self.messages:
            self.generate_all_messages()
        
        if test_mode:
            print("🧪 TEST MODE - No actual emails will be sent")
            print("="*50)
            
            for msg in self.messages[:3]:  # Show first 3 as examples
                print(f"TO: {msg['email']}")
                print(f"SUBJECT: Follow-up from our recent event")
                print(f"MESSAGE: {msg['message']}")
                print("-" * 30)
            
            print(f"... and {len(self.messages) - 3} more messages")
            return True
        
        # Real email sending (requires valid credentials)
        if not sender_email or not sender_password:
            print("❌ Error: Email credentials required for live sending")
            return False
        
        try:
            # Setup SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            
            sent_count = 0
            for msg in self.messages:
                try:
                    # Create email
                    email_msg = MIMEMultipart()
                    email_msg['From'] = sender_email
                    email_msg['To'] = msg['email']
                    email_msg['Subject'] = "Follow-up from our recent event"
                    
                    email_msg.attach(MIMEText(msg['message'], 'plain'))
                    
                    # Send email
                    server.sendmail(sender_email, msg['email'], email_msg.as_string())
                    sent_count += 1
                    print(f"✅ Sent to {msg['email']}")
                    
                except Exception as e:
                    print(f"❌ Failed to send to {msg['email']}: {str(e)}")
            
            server.quit()
            print(f"📧 Successfully sent {sent_count}/{len(self.messages)} emails")
            return True
            
        except Exception as e:
            print(f"❌ SMTP Error: {str(e)}")
            return False
    
    def create_telegram_batch(self, output_file='telegram_messages.json'):
        """Create a batch-ready script for Telegram bot queue"""
        if not self.messages:
            self.generate_all_messages()
        
        telegram_batch = {
            "bot_name": "EventFollowUpBot",
            "created_at": datetime.now().isoformat(),
            "total_messages": len(self.messages),
            "messages": []
        }
        
        for msg in self.messages:
            telegram_batch["messages"].append({
                "recipient_email": msg['email'],
                "recipient_name": msg['name'],
                "message_text": msg['message'],
                "priority": "high" if msg['has_joined_event'] else "normal",
                "tags": ["event_followup", "automated"]
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(telegram_batch, f, indent=2, ensure_ascii=False)
        
        print(f"📱 Telegram batch file created: {output_file}")
        return output_file

def main():
    """Main function to run the personalized messaging script"""
    print("🚀 Starting Personalized Messaging Script")
    print("="*50)
    
    # Initialize messenger with cleaned data
    messenger = PersonalizedMessenger('cleaned_output.csv')
    
    # Generate all personalized messages
    print("📝 Generating personalized messages...")
    messages = messenger.generate_all_messages()
    print(f"✅ Generated {len(messages)} personalized messages")
    
    # Save in different formats
    print("\n💾 Saving messages in multiple formats...")
    messenger.save_messages_csv()
    messenger.save_messages_json()
    messenger.save_messages_txt()
    
    # Demo email sending (test mode)
    print("\n📧 Demo: Email sending simulation...")
    messenger.send_email_smtp(test_mode=True)
    
    # Create Telegram batch
    print("\n📱 Creating Telegram bot batch file...")
    messenger.create_telegram_batch()
    
    print("\n✨ All tasks completed successfully!")
    print("\nFiles created:")
    print("- personalized_messages.csv (required deliverable)")
    print("- personalized_messages.json (bonus format)")
    print("- personalized_messages.txt (bonus format)")
    print("- telegram_messages.json (automation bonus)")
    
    # Show some example messages
    print("\n📋 Sample Messages:")
    print("-" * 30)
    for i, msg in enumerate(messages[:2]):
        print(f"To: {msg['email']}")
        print(f"Message: {msg['message']}")
        print("-" * 30)

if __name__ == "__main__":
    main()