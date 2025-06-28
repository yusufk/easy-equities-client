# Easy Equities and Satrix Python Client, with MCP server

Unofficial Python client for [Easy Equities](easyequities.io/) and 
[Satrix](satrix.co.za/). **Intended for personal use.**

Supports Python 3.6+.

[Pypi](https://pypi.org/project/easy-equities-client/)


## Installation

You can install the library from PyPI:

```
pip install easy-equities-client
```

**However, if you prefer to manage credentials and configuration yourself (recommended for development or advanced use), you can use the source directly:**

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/easy-equities-client.git
   cd easy-equities-client
   ```

2. (Optional) Create a virtual environment and activate it:

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Use the code directly from the cloned folder, or run scripts and the MCP server as described below.

---

## Features

Accounts:
- Get accounts for a user: `client.accounts.list()`
- Get account holdings: `client.accounts.holdings(account.id)`
- Get account valuations: `client.accounts.valuations(account.id)`
- Get account transactions: `client.accounts.transactions(account.id)`

Instruments:
- Get the historical prices for an instrument: 
  `client.instruments.historical_prices('EQU.ZA.SYGJP', Period.ONE_MONTH)`

## Usage

```python
from easy_equities_client.clients import EasyEquitiesClient # or SatrixClient

client = EasyEquitiesClient()
client.login(username='your username', password='your password')

# List accounts
accounts = client.accounts.list()
"""
[
    Account(id='12345', name='EasyEquities ZAR', trading_currency_id='2'),
    Account(id='12346', name='TFSA', trading_currency_id='3'),
    ...
]
"""

# Get account holdings
holdings = client.accounts.holdings(accounts[0].id)
"""
[
    {
        "name": "CoreShares Global DivTrax ETF",
        "contract_code": "EQU.ZA.GLODIV",
        "purchase_value": "R2 000.00",
        "current_value": "R3 000.00",
        "current_price": "R15.50",
        "img": "https://resources.easyequities.co.za/logos/EQU.ZA.GLODIV.png",
        "view_url": "/AccountOverview/GetInstrumentDetailAction/?IsinCode=ZAE000254249",
        "isin": "ZAE000254249"
    },
    ...
]
"""
# Optionally include number of shares for each holding (creates another API call for each holding)
holdings = client.accounts.holdings(accounts[0].id, include_shares=True)
"""
[
    {
        "name": "CoreShares Global DivTrax ETF",
        "contract_code": "EQU.ZA.GLODIV",
        "purchase_value": "R2 000.00",
        "current_value": "R3 000.00",
        "current_price": "R15.50",
        "img": "https://resources.easyequities.co.za/logos/EQU.ZA.GLODIV.png",
        "view_url": "/AccountOverview/GetInstrumentDetailAction/?IsinCode=ZAE000254249",
        "isin": "ZAE000254249",
        "shares": "200.123"
    },
    ...
]
"""

# Get account valuations
valuations = client.accounts.valuations(accounts[0].id)
"""
{
    "TopSummary": {
        "AccountValue": 300000.50,
        "AccountCurrency": "ZAR",
        "AccountNumber": "EE123456-111111",
        "AccountName": "EasyEquities ZAR",
        "PeriodMovements": [
            {
                "ValueMoveLabel": "Profit & Loss Value",
                "ValueMove": "R5 000.00",
                "PercentageMoveLabel": "Profit & Loss",
                "PercentageMove": "15.00%",
                "PeriodMoveHeader": "Movement on Current Holdings:"
            }
        ]
    },
    "NetInterestOnCashItems": [
        {
            "Label": "Total Interest on Free Cash",
            "Value": "R10.55"
        },
        ...
    ],
    "AccrualSummaryItems": [
        {
            "Label": "Net Accrual",
            "Value": "R2.00"
        },
        ...
    ],
    ...
}
"""

# Get account transactions
transactions = client.accounts.transactions(accounts[0].id)
"""
[
    {
        "TransactionId": 0,
        "DebitCredit": 200.00,
        "Comment": "Account Balance Carried Forward",
        "TransactionDate": "2020-07-21T01:00:00",
        "LogId": 123456789,
        "ActionId": 0,
        "Action": "Account Balance Carried Forward",
        "ContractCode": ""
    },
        {
        "TransactionId": 0,
        "DebitCredit": 50.00,
        "Comment": "CoreShares Global DivTrax ETF-Foreign Dividends @15.00",
        "TransactionDate": "2020-11-19T14:30:00",
        "LogId": 123456790,
        "ActionId": 122,
        "Action": "Foreign Dividend",
        "ContractCode": "EQU.ZA.GLODIV"
    },
    ...
]
"""

# Get historical data for an equity/instrument
from easy_equities_client.instruments.types import Period
historical_prices = client.instruments.historical_prices('EQU.ZA.SYGJP', Period.ONE_MONTH)
"""
{
    "chartData": {
        "Dataset": [
            41.97,
            42.37,
            ...
        ],
        "Labels": [
            "25 Jun 21",
            "28 Jun 21",
            ...
        ],
        "TradingCurrencySymbol": "R",
        ...
    }
}
"""
```

## Example Use Cases

### Show holdings total profits/losses

Run a script to show your holdings and their total profits/losses, e.g.  
[show_holdings_profit_loss.py](https://github.com/delenamalan/easy-equities-client/blob/master/examples/show_holdings_profit_loss.py).

![show_holdings_profit_loss.py example output](https://raw.githubusercontent.com/delenamalan/easy-equities-client/master/examples/show_holdings_profit_loss_example.png)



## Contributing

See [Contributing](./CONTRIBUTING.md)

## MCP Server

This fork adds an [MCP server](https://github.com/multimodal-cognition/mcp) that wraps the Easy Equities client, exposing its functionality as tools for LLM agents such as [Claude](https://claude.ai/) and the [`q` CLI](https://github.com/multimodal-cognition/q).

### Demo

Below is a demo of using the MCP server with the `q` CLI:

![q-mcp-demo](examples/easyequitiesmcp.gif)

### Running the MCP Server

First, ensure you have your Easy Equities credentials in a `.env` file:

```
EASYEQUITIES_USERNAME=your_username
EASYEQUITIES_PASSWORD=your_password
```

Then start the MCP server:

```sh
python mcp_server/mcp_server.py
```

Or, if you use a task runner or the `q` CLI, you can define it like this:

```json
"mcp_server": {
  "command": "python",
  "args": [
    "~/easy-equities-client/mcp_server/mcp_server.py"
  ],
  "cwd": "~/easy-equities-client"
}
```

### Using with Claude

You can connect Claude to your running MCP server and ask questions like:

- "List all my Easy Equities accounts."
- "Show the holdings for account 12345."
- "Get the historical prices for EQU.ZA.SYGJP over the last month."

Claude will call the appropriate MCP tools and return the results.

### Using with the `q` CLI

To use the MCP server with the [`q` CLI](https://github.com/multimodal-cognition/q), add the following entry to your `~/.aws/amazonq/mcp.json` file:

```json
"mcp_server": {
  "command": "python",
  "args": [
    "/Users/yusuf/Development/easy-equities-client/mcp_server/mcp_server.py"
  ],
  "cwd": "/Users/yusuf/Development/easy-equities-client"
}
```

Once this is configured, simply launch `q` and interact with your Easy Equities data in natural language.

---

See [mcp_server/mcp_server.py](./mcp_server/mcp_server.py) for available tool methods and their descriptions.
