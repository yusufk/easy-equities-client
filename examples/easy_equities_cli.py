#!/usr/bin/env python3
"""
Unified command-line interface for Easy Equities operations.
"""
import os
import json
from typing import Dict, Any
import argparse
from dotenv import load_dotenv
import colorama

from easy_equities_client.clients import EasyEquitiesClient
from easy_equities_client.instruments.types import Period

# Initialize colorama for colored output
colorama.init(autoreset=True)

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

def convert_to_float(value: str) -> float:
    """Get the float value from currency string, e.g. 'R9 323.46'"""
    return float(value[1:].replace(' ', ''))

def show_profit_loss(client: EasyEquitiesClient, account_id: str = None) -> None:
    """Show profit/loss for holdings in all accounts or a specific account"""
    accounts = client.accounts.list()
    
    for account in accounts:
        print(f"\n# {account.name}")
        # Go through each holding
        try:
            print(f"\nFetching holdings for {account.name}...")
            holdings = client.accounts.holdings(account.id)
            print(f"Found {len(holdings)} holdings")
            
            total_profit_loss = 0
            total_investment = 0

            for holding in holdings:
                try:
                    print(f"- {holding['name']}: ", end='')
                    currency = holding['purchase_value'][0]
                    purchase_value = convert_to_float(holding['purchase_value'])
                    current_value = convert_to_float(holding['current_value'])
                    profit_loss = current_value - purchase_value

                    total_profit_loss += profit_loss
                    total_investment += purchase_value
                    
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

            # Print total for this account
            if total_investment > 0:
                total_perc = (total_profit_loss / total_investment) * 100
                total_color = colorama.Fore.GREEN if total_profit_loss >= 0 else colorama.Fore.RED
                print(f"\nTotal for {account.name}: ", end='')
                print(total_color + f"{'+' if total_profit_loss >= 0 else '-'}R{abs(total_profit_loss):.2f} ({total_perc:.2f}%)")
            print()
        except Exception as e:
            print(f"Error fetching holdings for account {account.name}: {e}\n")

def show_historical_prices(client: EasyEquitiesClient, contract_code: str, period_str: str) -> None:
    """Show historical prices for an instrument"""
    try:
        period = Period[period_str.upper()]
    except KeyError:
        print(f"Error: Invalid period. Choose from: {', '.join(p.name for p in Period)}")
        return

    prices = client.instruments.historical_prices(contract_code, period)
    print(f"\nHistorical Prices for {contract_code} ({period.value}):")
    print_json(prices)

def main():
    parser = argparse.ArgumentParser(description="EasyEquities CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Account commands
    accounts_parser = subparsers.add_parser("accounts", help="Account operations")
    accounts_subparsers = accounts_parser.add_subparsers(dest="operation", help="Operation to perform")

    # List accounts
    accounts_subparsers.add_parser("list", help="List all accounts")

    # Valuations
    valuations_parser = accounts_subparsers.add_parser("valuations", help="Show account valuations")
    valuations_parser.add_argument("--account-id", "-a", required=True, help="Account ID")

    # Transactions
    transactions_parser = accounts_subparsers.add_parser("transactions", help="Show account transactions")
    transactions_parser.add_argument("--account-id", "-a", required=True, help="Account ID")

    # Holdings
    holdings_parser = accounts_subparsers.add_parser("holdings", help="Show account holdings")
    holdings_parser.add_argument("--account-id", "-a", required=True, help="Account ID")
    holdings_parser.add_argument("--include-shares", "-s", action="store_true", 
                               help="Include share counts (may be slower)")
                               
    # Profit/Loss
    profit_loss_parser = accounts_subparsers.add_parser("profit-loss", help="Show profit/loss for holdings")
    profit_loss_parser.add_argument("--account-id", "-a", help="Account ID (optional, shows all accounts if not specified)")

    # Instrument commands
    instruments_parser = subparsers.add_parser("instruments", help="Instrument operations")
    instruments_subparsers = instruments_parser.add_subparsers(dest="operation", help="Operation to perform")

    # Historical prices
    prices_parser = instruments_subparsers.add_parser("prices", help="Show historical prices")
    prices_parser.add_argument("contract_code", help="Contract code (e.g. EQU.ZA.SYGJP)")
    prices_parser.add_argument("--period", "-p", choices=[p.name for p in Period], default="ONE_MONTH",
                             help="Time period for historical data")

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

    if not args.command:
        parser.print_help()
        exit(1)

    # Handle account operations
    if args.command == "accounts":
        if not args.operation:
            accounts_parser.print_help()
            exit(1)

        if args.operation == "list":
            list_accounts(client)
        elif args.operation == "valuations":
            show_valuations(client, args.account_id)
        elif args.operation == "transactions":
            show_transactions(client, args.account_id)
        elif args.operation == "holdings":
            show_holdings(client, args.account_id, args.include_shares)
        elif args.operation == "profit-loss":
            show_profit_loss(client, args.account_id)

    # Handle instrument operations
    elif args.command == "instruments":
        if not args.operation:
            instruments_parser.print_help()
            exit(1)

        if args.operation == "prices":
            show_historical_prices(client, args.contract_code, args.period)

if __name__ == "__main__":
    main()
