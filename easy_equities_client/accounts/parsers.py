from dataclasses import dataclass
from typing import List, Optional

from bs4 import BeautifulSoup
from bs4.element import Tag

from easy_equities_client.accounts.types import Account, Holding


def extract_account_info(account_div: Tag) -> Optional[Account]:
    trading_currency = account_div.parent.attrs.get("data-tradingcurrencyid")
    if not trading_currency:
        return None
    return Account(
        name=account_div.text.strip(),
        trading_currency_id=trading_currency.strip(),
        id=account_div.parent.attrs["data-id"].strip(),
    )


@dataclass
class AccountOverviewParser:
    """
    Parse the accounts overview page (/AccountOverview) given the html
    contents of the page.
    """

    page: str

    def extract_accounts(self) -> List[Account]:
        """
        Return the accounts found on the account overview page.
        """
        soup = BeautifulSoup(self.page, "html.parser")
        accounts_divs = soup.find_all(attrs={"id": "trust-account-types"})
        return [
            account
            for account in [
                extract_account_info(account_div) for account_div in accounts_divs
            ]
            if account
        ]


class HoldingFieldNotFoundException(Exception):
    def __init__(self, field, exception):
        return super().__init__(
            f"Field '{field}' not found in holding div. Exception: f{exception}"
        )


class HoldingDivParser:
    def __init__(self, div: Tag):
        self.div = div

    def __eq__(a, b):
        return a.name == b.name

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self) -> str:
        # First try to find the equity-image-as-text div
        name_div = self.div.find(attrs={'class': 'equity-image-as-text'})
        if name_div:
            # Find the inner div that contains the name text
            inner_div = name_div.find('div', attrs={'class': 'auto-ellipsis'})
            if inner_div:
                # Get the text from the innermost div
                inner_text_div = inner_div.find('div')
                if inner_text_div:
                    return inner_text_div.text.strip()
                return inner_div.text.strip()
            return name_div.text.strip()
        
        # Debug logging for HTML structure
        debug_html = "Could not get HTML"
        try:
            debug_html = str(self.div.prettify())[:500]
        except:
            pass
        raise ValueError(f"Could not find name in holding div. HTML structure: {debug_html}")

    def _find_cell_value(self, class_name: str) -> str:
        cell = self.div.find(attrs={'class': class_name})
        if cell:
            value = cell.find('span')
            if value:
                return value.text.strip()
            return cell.text.strip()
        return "0"

    @property
    def purchase_value(self) -> str:
        return self._find_cell_value('purchase-value-cell')

    @property
    def current_value(self) -> str:
        return self._find_cell_value('current-value-cell')

    @property
    def current_price(self) -> str:
        return self._find_cell_value('current-price-cell')

    @property
    def img(self) -> str:
        img = self.div.find(attrs={'class': 'instrument'})
        return img.attrs['src'] if img and 'src' in img.attrs else ""

    @property
    def contract_code(self) -> str:
        if not self.img:
            return ""
        try:
            filename = self.img[self.img.rindex('/') + 1:]
            return filename[:filename.rindex('.')] if '.' in filename else filename
        except ValueError:
            return ""

    @property
    def view_url(self) -> str:
        try:
            container = self.div.find(attrs={'class': 'collapse-container'})
            if container:
                span = container.find('span')
                if span and 'data-detailviewurl' in span.attrs:
                    return span.attrs['data-detailviewurl']
        except (AttributeError, KeyError):
            pass
        return ""

    @property
    def isin(self) -> str:
        url = self.view_url
        if url and '=' in url:
            return url.split('=')[-1]
        return ""

    def to_dict(self) -> Holding:
        fields = [
            'name',
            'contract_code',
            'purchase_value',
            'current_value',
            'current_price',
            'img',
            'view_url',
            'isin',
        ]
        data: Holding = {}
        for field in fields:
            try:
                data[field] = getattr(self, field)  # type: ignore
            except Exception as e:
                raise HoldingFieldNotFoundException(field, e)

        return data

    def _find_cell_value(self, class_name: str) -> str:
        cell = self.div.find(attrs={'class': class_name})
        if cell:
            value = cell.find('span')
            if value:
                return value.text.strip()
            return cell.text.strip()
        return "0"

    @property
    def purchase_value(self) -> str:
        return self._find_cell_value('purchase-value-cell')

    @property
    def current_value(self) -> str:
        return self._find_cell_value('current-value-cell')

    @property
    def current_price(self) -> str:
        return self._find_cell_value('current-price-cell')

    @property
    def img(self) -> str:
        img = self.div.find(attrs={'class': 'instrument'})
        return img.attrs['src'] if img and 'src' in img.attrs else ""

    @property
    def contract_code(self) -> str:
        if not self.img:
            return ""
        try:
            filename = self.img[self.img.rindex('/') + 1:]
            return filename[:filename.rindex('.')] if '.' in filename else filename
        except ValueError:
            return ""

    @property
    def view_url(self) -> str:
        try:
            container = self.div.find(attrs={'class': 'collapse-container'})
            if container:
                span = container.find('span')
                if span and 'data-detailviewurl' in span.attrs:
                    return span.attrs['data-detailviewurl']
        except (AttributeError, KeyError):
            pass
        return ""

    @property
    def isin(self) -> str:
        url = self.view_url
        if url and '=' in url:
            return url.split('=')[-1]
        return ""

    def to_dict(self) -> Holding:
        fields = [
            'name',
            'contract_code',
            'purchase_value',
            'current_value',
            'current_price',
            'img',
            'view_url',
            'isin',
        ]
        data: Holding = {}
        for field in fields:
            try:
                data[field] = getattr(self, field)  # type: ignore
            except Exception as e:
                raise HoldingFieldNotFoundException(field, e)

        return data

    def _find_cell_value(self, class_name: str) -> str:
        cell = self.div.find(attrs={'class': class_name})
        if cell:
            value = cell.find('span')
            if value:
                return value.text.strip()
            return cell.text.strip()
        return "0"

    @property
    def purchase_value(self) -> str:
        return self._find_cell_value('purchase-value-cell')

    @property
    def current_value(self) -> str:
        return self._find_cell_value('current-value-cell')

    @property
    def current_price(self) -> str:
        return self._find_cell_value('current-price-cell')

    @property
    def img(self) -> str:
        img = self.div.find(attrs={'class': 'instrument'})
        return img.attrs['src'] if img and 'src' in img.attrs else ""

    @property
    def contract_code(self) -> str:
        if not self.img:
            return ""
        try:
            filename = self.img[self.img.rindex('/') + 1:]
            return filename[:filename.rindex('.')] if '.' in filename else filename
        except ValueError:
            return ""

    @property
    def view_url(self) -> str:
        try:
            container = self.div.find(attrs={'class': 'collapse-container'})
            if container:
                span = container.find('span')
                if span and 'data-detailviewurl' in span.attrs:
                    return span.attrs['data-detailviewurl']
        except (AttributeError, KeyError):
            pass
        return ""

    @property
    def isin(self) -> str:
        url = self.view_url
        if url and '=' in url:
            return url.split('=')[-1]
        return ""

    def to_dict(self) -> Holding:
        fields = [
            'name',
            'contract_code',
            'purchase_value',
            'current_value',
            'current_price',
            'img',
            'view_url',
            'isin',
        ]
        data: Holding = {}
        for field in fields:
            try:
                data[field] = getattr(self, field)  # type: ignore
            except Exception as e:
                raise HoldingFieldNotFoundException(field, e)

        return data


@dataclass
class AccountHoldingsParser:
    """
    Parse the accounts holdings page given the html contents of the page.
    """

    page: bytes

    def extract_holdings(self) -> List[Holding]:
        """
        Return the holdings found on the holdings page.
        """
        soup = BeautifulSoup(self.page, "html.parser")
        # Get all holding containers that are not in the header
        holdings_divs = []
        table_body = soup.find(attrs={'class': 'holding-table-body'})
        if table_body:
            for holding_row in table_body.find_all('div', attrs={'class': 'holding-body-table-row'}):
                container = holding_row.find('div', attrs={'class': 'display-flex-justify-content-space-between-align-items-center'})
                if container and 'holding-inner-container' in container.get('class', []):
                    holdings_divs.append(container)
        divs = set([HoldingDivParser(holding_div) for holding_div in holdings_divs])
        return [div.to_dict() for div in divs]
