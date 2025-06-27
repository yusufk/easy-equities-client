# An MCP server that wraps the easy-equities functionality
from mcp.server.fastmcp import FastMCP
from easy_equities_client.clients import EasyEquitiesClient
import os
from dotenv import load_dotenv
import logging
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load credentials from .env
load_dotenv()
username = os.getenv("EASYEQUITIES_USERNAME")
password = os.getenv("EASYEQUITIES_PASSWORD")

if not username or not password:
    raise Exception("Please set EASYEQUITIES_USERNAME and EASYEQUITIES_PASSWORD in your .env file")

client = EasyEquitiesClient()
client.login(username=username, password=password)

# Create an MCP server
mcp = FastMCP("EasyEquities")

logging.basicConfig(level=logging.DEBUG)


@mcp.tool()
def list_accounts() -> list:
    logging.info("list_accounts called")
    """List all Easy Equities accounts with correct attribute names"""
    accounts = client.accounts.list()
    return [
        {
            "account_id": account.id,
            "account_name": account.name,
            "trading_currency_id": account.trading_currency_id
        }
        for account in accounts
    ]


@mcp.tool()
def get_account_valuations(account_id: str) -> dict:
    logging.info(f"get_account_valuations called with account_id={account_id}")
    """Get valuations for a specific Easy Equities account"""
    try:
        return client.accounts.valuations(account_id)
    except Exception as e:
        logging.error(f"Error getting valuations for account {account_id}: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def get_account_transactions(account_id: str) -> dict:
    logging.info(f"get_account_transactions called with account_id={account_id}")
    """Get transaction history for a specific Easy Equities account"""
    try:
        return client.accounts.transactions(account_id)
    except Exception as e:
        logging.error(f"Error getting transactions for account {account_id}: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def get_account_holdings(account_id: str, include_shares: bool = False) -> dict:
    logging.info(f"get_account_holdings called with account_id={account_id}, include_shares={include_shares}")
    """Get current holdings for a specific Easy Equities account"""
    try:
        return client.accounts.holdings(account_id, include_shares)
    except Exception as e:
        logging.error(f"Error getting holdings for account {account_id}: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def get_instrument_historical_prices(contract_code: str, period: str = "ONE_MONTH") -> dict:
    logging.info(f"get_instrument_historical_prices called with contract_code={contract_code}, period={period}")
    """Get historical prices for an instrument. Available periods: ONE_DAY, ONE_WEEK, ONE_MONTH, THREE_MONTHS, SIX_MONTHS, ONE_YEAR, TWO_YEARS, FIVE_YEARS"""
    try:
        from easy_equities_client.instruments.types import Period
        # Convert string to enum, handling case variations
        period_upper = period.upper().replace(" ", "_")
        if not hasattr(Period, period_upper):
            available_periods = [p.name for p in Period]
            return {"error": f"Invalid period '{period}'. Available periods: {available_periods}"}
        
        period_enum = Period[period_upper]
        return client.instruments.historical_prices(contract_code, period_enum)
    except Exception as e:
        logging.error(f"Error getting historical prices for {contract_code}: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def get_account_summary() -> dict:
    """Get a summary of all accounts with basic information"""
    logging.info("get_account_summary called")
    try:
        accounts = client.accounts.list()
        summary = {
            "total_accounts": len(accounts),
            "accounts": []
        }
        
        for account in accounts:
            account_info = {
                "account_id": account.id,
                "account_name": account.name,
                "trading_currency_id": account.trading_currency_id
            }
            
            # Try to get basic valuation info
            try:
                valuations = client.accounts.valuations(account.id)
                if isinstance(valuations, dict) and 'totalValue' in valuations:
                    account_info["total_value"] = valuations.get('totalValue')
                    account_info["currency"] = valuations.get('currency', 'Unknown')
            except Exception as e:
                logging.warning(f"Could not get valuations for account {account.id}: {str(e)}")
                account_info["valuation_error"] = str(e)
            
            summary["accounts"].append(account_info)
        
        return summary
    except Exception as e:
        logging.error(f"Error getting account summary: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()