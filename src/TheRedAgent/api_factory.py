from FinAPIWrapper import FinancialModelingPrepAPI
from FinMockAPIWrapper import FinMockAPIWrapper

def get_api_wrapper(use_mock=False, api_key=None):
    """
    Factory function to return the appropriate API wrapper.
    :param use_mock: If True, return the mock API wrapper.
    :param api_key: API key for the real API (ignored if use_mock is True).
    """
    if use_mock:
        return FinMockAPIWrapper()
    else:
        if api_key is None:
            raise ValueError("API key must be provided when using the real API.")
        return FinancialModelingPrepAPI(api_key=api_key)
