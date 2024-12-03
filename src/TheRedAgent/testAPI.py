from api_factory import get_api_wrapper

# api = get_api_wrapper(use_mock=True)  # Mock
api = get_api_wrapper(use_mock=False, api_key="random")  # Real API

'''
query = "Apple"
result = api.search_company(query)
if result:
    print("Search Results:", result)
else:
    print("No results or an error occurred.")
'''

top_gainers = api.get_top_gainers()
if top_gainers:
    for i, gainer in enumerate(top_gainers, 1):
        ticker = gainer.get("name", "Unknown Name")
        change = gainer.get("changesPercentage", "Unknown Change")
        print(f"{i}. {ticker}: {change}%")
else:
    print("No data found or an error occurred.")
