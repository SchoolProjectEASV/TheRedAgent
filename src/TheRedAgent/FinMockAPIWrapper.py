class FinMockAPIWrapper:
    def search_company(self, query: str):
        """
        Mock method for searching a company.
        :param query: Company name or ticker to search for.
        :return: Mocked JSON response.
        """
        return [
            {
                "ticker": "MOCK1",
                "name": f"Mock Company {query}",
                "sector": "Technology",
            },
            {
                "ticker": "MOCK2",
                "name": f"Another Mock Company {query}",
                "sector": "Finance",
            },
            {
                "ticker": "MOCK3",
                "name": f"Jens Issa IT-Service {query}",
                "sector": "Technology",
            },
            {"ticker": "MOCK2", "name": f"Mock company 4 {query}", "sector": "Finance"},
            {
                "ticker": "MOCK2",
                "name": f"Mock company number 5 {query}",
                "sector": "Healthcare",
            },
        ]

    def get_top_gainers(self, limit=5):
        mock_data = [
            {"name": "META", "changesPercentage": "+5.0"},
            {"name": "AMAZON", "changesPercentage": "+4.5"},
            {"name": "NVDIA", "changesPercentage": "+7.6"},
            {"name": "MAERSK", "changesPercentage": "+3.2"},
            {"name": "STEAM", "changesPercentage": "+4.1"},
        ]

        sorted_data = sorted(
            mock_data,
            key=lambda x: float(x["changesPercentage"].strip("+").strip("%")),
            reverse=True,
        )

        return sorted_data[:limit]
