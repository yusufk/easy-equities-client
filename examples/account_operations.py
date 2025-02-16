"""
Interactive script to run any of the account client functions.
"""
import os
from typing import Dict, Any
import json
from dotenv import load_dotenv
import argparse

from easy_equities_client.clients import EasyEquitiesClient
from easy_equities_client.accounts.types import Account

def print_json(data: Dict[str, Any]) -> None:
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def list_accounts(client: EasyEquitiesClient) -> None:
    """List all accounts"""
    accounts = client.accounts.list()
    print("\nAvailable Accounts:")
    for account in accounts:
        print(f"- {account.name} (ID: {account.id})")
    return accounts

def show_valuations(client: EasyEquitiesClient, account_id: str) -> None:
    """Show account valuations"""
    valuations = client.accounts.valuations(account_id)
    print("\nAccount Valuations:")
    print_json(valuations)

def show_transactions(client: EasyEquitiesClient, account_id: str) -> None:
    """Show account transactions"""
    transactions = client.accounts.transactions(account_id)
    print("\nAccount Transactions:")
    print_json(transactions)

def show_holdings(client: EasyEquitiesClient, account_id: str, include_shares: bool = False) -> None:
    """Show account holdings"""
    holdings = client.accounts.holdings(account_id, include_shares)
    print("\nAccount Holdings:")
    print_json(holdings)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="EasyEquities Account Operations")
    parser.add_argument("operation", choices=["list", "valuations", "transactions", "holdings"],
                      help="Operation to perform")
    parser.add_argument("--account-id", "-a", help="Account ID (required for all operations except list)")
    parser.add_argument("--include-shares", "-s", action="store_true", 
                      help="Include share counts in holdings (may be slower)")
    args = parser.parse_args()

    # Load credentials and initialize client
    load_dotenv()
    username = os.getenv("EASYEQUITIES_USERNAME")
    password = os.getenv("EASYEQUITIES_PASSWORD")

    if not username or not password:
        print("Error: Please set EASYEQUITIES_USERNAME and EASYEQUITIES_PASSWORD in your .env file")
        exit(1)

    client = EasyEquitiesClient()
    client.login(username=username, password=password)

    # Execute requested operation
    if args.operation == "list":
        list_accounts(client)
    else:
        if not args.account_id:
            accounts = list_accounts(client)
            account_id = input("\nEnter account ID from the list above: ")
        else:
            account_id = args.account_id

        if args.operation == "valuations":
            show_valuations(client, account_id)
        elif args.operation == "transactions":
            show_transactions(client, account_id)
        elif args.operation == "holdings":
            show_holdings(client, account_id, args.include_shares)

if __name__ == "__main__":
    main()
