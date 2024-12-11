import requests
from urllib.parse import urlencode


class FinancialModelingPrepAPI:
    BASE_URL = "https://financialmodelingprep.com/api/v3/stock_market"

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()  # Clean up the API key

    def search_company(self, query: str):
        url = f"{self.BASE_URL}/search"
        params = {"query": query, "apikey": self.api_key}

        # Log the constructed URL
        print(f"Constructed URL: {url}?{urlencode(params)}")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_top_gainers(self, limit=5):
        url = f"{self.BASE_URL}/gainers"
        params = {"apikey": self.api_key}

        # Log the constructed URL
        print(f"Constructed URL: {url}?{urlencode(params)}")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            gainers = response.json()
            return gainers[:limit]
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_top_losers(self, limit=5):
        url = f"{self.BASE_URL}/losers"
        params = {"apikey": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            losers = response.json()
            return losers[:limit]
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
