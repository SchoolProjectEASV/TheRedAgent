import requests


class FinancialModelingPrepAPI:
    BASE_URL = "https://financialmodelingprep.com/api/v3/stock_market"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_company(self, query: str):
        url = f"{self.BASE_URL}/search"
        params = {"query": query, "apikey": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_top_gainers(self, limit=5):
        
        #Fetch the top gainers in the stock market today.
        url = f"{self.BASE_URL}/gainers"
        params = {"apikey": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            gainers = response.json()
            return gainers[:limit]  # Return the top gainers
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None