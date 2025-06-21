# An MCP server that wraps the easy-equitties functionality
from mcp.server.fastmcp import FastMCP
from easy_equities_client.clients import EasyEquitiesClient
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
username = os.getenv("EASYEQUITIES_USERNAME")
password = os.getenv("EASYEQUITIES_PASSWORD")

if not username or not password:
    raise Exception("Please set EASYEQUITIES_USERNAME and EASYEQUITIES_PASSWORD in your .env file")

client = EasyEquitiesClient()
client.login(username=username, password=password)

# Create an MCP server
mcp = FastMCP("Demo")


@mcp.tool()
def list_accounts() -> list:
    """List all accounts"""
    return [account.__dict__ for account in client.accounts.list()]


@mcp.tool()
def get_account_valuations(account_id: str) -> dict:
    """Get valuations for an account"""
    return client.accounts.valuations(account_id)


@mcp.tool()
def get_account_transactions(account_id: str) -> dict:
    """Get transactions for an account"""
    return client.accounts.transactions(account_id)


@mcp.tool()
def get_account_holdings(account_id: str, include_shares: bool = False) -> dict:
    """Get holdings for an account"""
    return client.accounts.holdings(account_id, include_shares)


@mcp.tool()
def get_instrument_historical_prices(contract_code: str, period: str = "ONE_MONTH") -> dict:
    """Get historical prices for an instrument"""
    from easy_equities_client.instruments.types import Period
    period_enum = Period[period.upper()]
    return client.instruments.historical_prices(contract_code, period_enum)