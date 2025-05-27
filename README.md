# Python-Automation-Scripting
# Python & Automation Intern Assignment

A comprehensive Python automation solution for event data processing, personalized messaging, and automated communication workflows.

## 🎯 Project Overview

This project demonstrates automation skills through real event data processing, including data cleaning, personalized message generation, and automated communication systems using Python.

**Estimated Development Time:** 3 hours  
**Dataset:** 600+ rows of event participant data

## 📁 Project Structure

```
python-automation-assignment/
├── README.md
├── cleaned_output.csv          # Cleaned dataset (provided)
├── personalized_messaging.py   # Step 2: Message generation script
├── automation_bonus.py         # Step 3: Automation features
├── personalized_messages.csv   # Generated messages (output)
├── personalized_messages.json  # Bonus: JSON format
├── personalized_messages.txt   # Bonus: Text format
└── telegram_queue.json         # Telegram bot queue (output)
```

## 🚀 Features

### ✅ Step 1: Data Cleaning (Completed)
- Removed duplicate email rows
- Normalized `has_joined_event` values (Yes/No → True/False)
- Flagged missing/incomplete LinkedIn profiles
- Flagged blank job titles
- Output: `cleaned_output.csv`

### ✅ Step 2: Auto-Personalized Messaging
- **Smart message generation** based on:
  - Event attendance status
  - Job title information
  - Name personalization
  - LinkedIn profile presence
- **Multiple output formats**:
  - CSV (required deliverable)
  - JSON (bonus)
  - TXT (bonus)

### ✅ Step 3: Automation Features (Bonus)
- **Email Automation**:
  - Gmail SMTP integration
  - Batch processing with rate limiting
  - HTML-formatted emails
  - Dry-run testing mode
- **Telegram Bot Integration**:
  - Priority-based message queuing
  - Automated scheduling
  - Retry logic implementation

## 🔧 Installation & Setup

### Prerequisites
```bash
pip install pandas smtplib json requests
```

### Environment Variables (Optional - for production)
```bash
export GMAIL_EMAIL="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export TELEGRAM_BOT_TOKEN="your-bot-token"
```

## 🏃‍♂️ Usage

### 1. Generate Personalized Messages
```bash
python personalized_messaging.py
```

**Output:**
- `personalized_messages.csv` (required deliverable)
- `personalized_messages.json` (bonus format)
- `personalized_messages.txt` (bonus format)

### 2. Run Automation Demo
```bash
python automation_bonus.py
```

**Features:**
- Email automation simulation
- Telegram bot queue creation
- Performance analytics

## 📊 Sample Output

### Message Examples

**For Event Attendees:**
```
🎉 Hey Venkatesh, thanks for joining our session! As a freelance developer, 
we think you'll love our upcoming AI workflow tools. Want early access?
```

**For Non-Attendees:**
```
Hi Arushi, sorry we missed you at the last event! We're preparing another 
session that might better suit your interests as a Product Manager. 
Hope to see you next time!
```

### CSV Output Format
```csv
email,message
venkatesh@gmail.com,"🎉 Hey Venkatesh, thanks for joining our session!..."
mark@gmail.com,"Hi Mark, sorry we missed you at the last event!..."
```

## 🤖 Automation Features

### Email Automation
- **Batch Processing**: Configurable batch sizes with delays
- **Rate Limiting**: Prevents spam detection
- **HTML Formatting**: Professional email templates
- **Error Handling**: Comprehensive logging and retry logic
- **Test Mode**: Safe dry-run functionality

### Telegram Integration
- **Priority Queuing**: High priority for event attendees
- **Smart Scheduling**: Delayed sending for non-attendees
- **JSON Queue Format**: Bot-ready message structure
- **Retry Logic**: Automatic failure handling

## 📈 Performance Metrics

- **Message Generation**: ~5 messages/second
- **Email Processing**: Configurable batch sizes (default: 10)
- **Success Tracking**: Detailed analytics and reporting
- **Error Handling**: Comprehensive failure management

## 🔒 Security Features

- **Environment Variables**: Secure credential management
- **Dry-run Mode**: Safe testing without actual sending
- **Input Validation**: Data sanitization and error checking
- **Rate Limiting**: API abuse prevention

## 🧪 Testing

### Run in Test Mode (Recommended)
```python
# Email testing
messenger.send_email_smtp(test_mode=True)

# Automation demo
python automation_bonus.py  # Runs in simulation mode by default
```

### Production Mode
```python
# Set dry_run=False for actual email sending
email_automation.send_batch_emails(dry_run=False)
```

## 📋 Assignment Compliance

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Data cleaning script | ✅ | `cleaned_output.csv` provided |
| Personalized messaging | ✅ | `personalized_messaging.py` |
| CSV output with email/message | ✅ | `personalized_messages.csv` |
| Bonus formats (TXT/JSON) | ✅ | Multiple output formats |
| SMTP email automation | ✅ | Gmail integration with batching |
| Telegram bot integration | ✅ | Queue system with priority |

## 🛠️ Technical Stack

- **Python 3.7+**
- **Libraries:**
  - `pandas` - Data processing and CSV handling
  - `smtplib` - Email automation
  - `json` - Data serialization
  - `requests` - API communication
  - `datetime` - Timestamp management

## 🚀 Future Enhancements

- [ ] Database integration for persistent storage
- [ ] Web dashboard for campaign management
- [ ] Advanced analytics and A/B testing
- [ ] Multi-language message support  
- [ ] Advanced scheduling algorithms
- [ ] Integration with CRM systems

## 📧 Contact

For questions about this implementation or the assignment, please reach out through the provided communication channels.

---

**Note:** This project demonstrates automation skills for internship evaluation. All email sending is in test mode by default to prevent accidental messaging.
