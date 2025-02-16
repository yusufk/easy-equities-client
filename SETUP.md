# Setup Guide

## Prerequisites
- Python 3.8+ (recommended)
- pip or poetry

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/easy-equities-client
cd easy-equities-client
```

2. Set up your environment:
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
# Using pip
pip install -r requirements.txt

# OR using poetry (recommended)
poetry install
```

4. Configure your credentials:
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your Easy Equities credentials
# Replace your_username and your_password with your actual credentials
```

## Security Notes

1. **Credential Storage**:
   - Credentials are stored locally in .env file
   - .env file is listed in .gitignore to prevent accidental commits
   - No credentials are sent to third parties

2. **Data Privacy**:
   - All API calls are made directly to Easy Equities servers
   - Data is not cached or stored locally
   - Communication uses HTTPS for security

3. **Best Practices**:
   - Never share your .env file
   - Don't commit credentials to git
   - Regularly update your password
   - Use a strong password

## Testing the Installation

Run the example script to verify your setup:

```bash
python examples/show_holdings_profit_loss.py
```

This will display your current holdings and their profit/loss status if configured correctly.

## Troubleshooting

1. If you get authentication errors:
   - Verify your credentials in .env are correct
   - Ensure you can log in to Easy Equities website

2. If you get dependency errors:
   - Make sure you're using Python 3.8+
   - Try reinstalling dependencies
   - Check if your virtual environment is activated
