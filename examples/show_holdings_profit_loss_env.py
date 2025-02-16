"""
Calculate the total profit/loss for each of your accounts using credentials from .env file.
"""
import os
from dotenv import load_dotenv
import colorama

from easy_equities_client.clients import (
    EasyEquitiesClient,
    PlatformClient,
    SatrixClient,
)

# Initialize colorama for colored output
colorama.init(autoreset=True)

# Load credentials from .env file
load_dotenv()
username = os.getenv("EASYEQUITIES_USERNAME")
password = os.getenv("EASYEQUITIES_PASSWORD")
platform = os.getenv("EASYEQUITIES_PLATFORM", "easyequities")  # Default to easyequities

if not username or not password:
    print("Error: Please set EASYEQUITIES_USERNAME and EASYEQUITIES_PASSWORD in your .env file")
    exit(1)

# Initialize the client
client: PlatformClient = (
    EasyEquitiesClient() if platform == 'easyequities' else SatrixClient()
)
client.login(username=username, password=password)

# List of accounts
accounts = client.accounts.list()

def convert_to_float(value: str) -> float:
    """
    Get the float value from, for example, "R9 323.46".
    """
    return float(value[1:].replace(' ', ''))

# Go through each account
for account in accounts:
    print(f"\n# {account.name}")
    # Go through each holding
    try:
        print(f"\nFetching holdings for {account.name}...")
        holdings = client.accounts.holdings(account.id)
        print(f"Found {len(holdings)} holdings")
        
        for holding in holdings:
            try:
                print(f"- {holding['name']}: ", end='')
                currency = holding['purchase_value'][0]
                purchase_value = convert_to_float(holding['purchase_value'])
                current_value = convert_to_float(holding['current_value'])
                profit_loss = current_value - purchase_value
                
                # Handle zero purchase value case
                if purchase_value == 0:
                    if current_value > 0:
                        profit_loss_perc = 100  # 100% gain if we got something from nothing
                    else:
                        profit_loss_perc = 0
                else:
                    profit_loss_perc = (profit_loss / purchase_value) * 100
                symbol = '+' if profit_loss >= 0 else '-'
                colour = colorama.Fore.GREEN if profit_loss >= 0 else colorama.Fore.RED

                str_profit_loss = (
                    f"{symbol}{currency}{abs(profit_loss):.2f} ({profit_loss_perc:.2f}%)"
                )
                print(colour + str_profit_loss)
            except Exception as e:
                print(f"Error processing holding: {str(e)}")
                print(f"Raw holding data: {holding}")
    except Exception as e:
        print(f"Error fetching holdings: {str(e)}")
    print("")
