import json
from typing import List, Optional

from bs4 import BeautifulSoup
from requests import Session

from easy_equities_client import constants
from easy_equities_client.accounts.parsers import (
    AccountHoldingsParser,
    AccountOverviewParser,
)
from easy_equities_client.accounts.types import Account, Holding, Transaction, Valuation
from easy_equities_client.types import Client


class AccountsClient(Client):
    def __init__(self, base_url: str = "", session: Session = None):
        super().__init__(base_url, session)
        self.current_account: Optional[str] = None

    def _get_account_overview_page(self) -> str:
        response = self.session.get(self._url(constants.PLATFORM_ACCOUNT_OVERVIEW_PATH))
        assert (
            response.status_code == 200
        ), "Account overview page should return 200 status code"
        assert "My Investments" in str(response.content)
        return str(response.content)

    def list(self) -> List[Account]:
        page = self._get_account_overview_page()
        parser = AccountOverviewParser(page)
        return parser.extract_accounts()

    def _switch_account(self, account_id: str) -> None:
        """
        Switch the currently selected account to account with ID account_id.
        """
        if self.current_account != account_id:
            data = {'trustAccountId': account_id}
            response = self.session.post(
                self._url(constants.PLATFORM_UPDATE_CURRENCY_PATH), data
            )
            response.raise_for_status()
            assert (
                response.status_code == 200
            ), "Update currency request should return 200 status code"
            self.current_account = account_id

    def valuations(self, account_id: str) -> Valuation:
        self._switch_account(account_id)
        response = self.session.get(
            self._url(constants.PLATFORM_ACCOUNT_VALUATIONS_PATH)
        )
        response.raise_for_status()
        return json.loads(response.json())

    def transactions(self, account_id) -> List[Transaction]:
        self._switch_account(account_id)
        response = self.session.get(self._url(constants.PLATFORM_TRANSACTIONS_PATH))
        response.raise_for_status()
        return response.json()

    def holdings(self, account_id: str, include_shares: bool = False) -> List[Holding]:
        """
        Get an account's holdings/stocks.

        :param account_id: String account ID.
        :param include_shares: Whether to fetch the number of shares per holding. Create an extra
        HTTP request per holding.
        """
        self._switch_account(account_id)
        response = self.session.get(self._url(constants.PLATFORM_HOLDINGS_PATH))
        response.raise_for_status()
        parser = AccountHoldingsParser(response.content)
        holdings = parser.extract_holdings()
        if include_shares:
            for holding in holdings:
                response = self.session.get(self._url(holding['view_url']))
                soup = BeautifulSoup(response.content, "html.parser")
                whole_shares = soup.find(
                    lambda tag: '#Shares' in tag
                ).next_sibling.next_sibling.text.strip()
                partial_shares = soup.find(
                    lambda tag: '#FSR' in tag
                ).next_sibling.next_sibling.text.strip()
                holding['shares'] = f"{whole_shares}{partial_shares}"
        return holdings

    def login(self) -> None:
        """
        Authenticates with EasyEquities using credentials from a .env file.
        The .env file should contain EASYEQUITIES_USERNAME and EASYEQUITIES_PASSWORD.
        """
        from dotenv import load_dotenv
        import os
        load_dotenv()
        username = os.getenv("EASYEQUITIES_USERNAME")
        password = os.getenv("EASYEQUITIES_PASSWORD")
        if not username or not password:
            raise ValueError("Username or password not set in the .env file.")
        login_url = "https://portfolio-overview.apps.easyequities.io/"
        payload = {"username": username, "password": password}
        response = self.session.post(login_url, data=payload)
        response.raise_for_status()
        assert "My Investments" in str(response.content), "Login failed"

    def get_statement_by_id(self, account_id: str, statement_id: str, save_path: str = None) -> dict:
        """
        Get a specific statement by ID for extended transaction history.
        Returns PDF content that can be saved or parsed.
        
        :param account_id: String account ID
        :param statement_id: Statement ID to fetch
        :param save_path: Optional path to save the PDF file
        """
        self._switch_account(account_id)
        # Extract account number from account info if needed
        account_number = f"EE565852-{account_id}"  # Format observed from curl
        import time
        timestamp = int(time.time() * 1000)
        
        url = f"{self._url(constants.PLATFORM_STATEMENT_BY_ID_PATH)}/{statement_id}"
        params = {
            'accountNumber': account_number,
            '_': timestamp
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(response.content)
        
        return {
            "statement_id": statement_id,
            "content_type": response.headers.get('content-type'),
            "content_length": len(response.content),
            "saved_to": save_path if save_path else None,
            "pdf_content": response.content if not save_path else None
        }

    def list_statements(self, account_id: str) -> list:
        """
        List available statements for an account by parsing the statements page.
        
        :param account_id: String account ID
        """
        self._switch_account(account_id)
        response = self.session.get(self._url(constants.PLATFORM_STATEMENTS_LIST_PATH))
        response.raise_for_status()
        
        # Parse statement IDs from the page content
        import re
        content = response.text
        statement_matches = re.findall(r'/Statement/GetStatementById/(\d+)', content)
        
        # Remove duplicates and sort (newest first, assuming higher IDs are newer)
        statement_ids = sorted(list(set(statement_matches)), key=int, reverse=True)
        
        return [{"statement_id": sid} for sid in statement_ids]
