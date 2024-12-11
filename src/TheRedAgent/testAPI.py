from api_factory import APIFactory

api = APIFactory.get_api_wrapper(use_mock=True)  # Mock
api = APIFactory.get_api_wrapper(use_mock=False, api_key="fn18vo1LrH6BLxdvhQvfSC8ALmgS170m")  # Real API

'''
query = "Apple"
result = api.search_company(query)
if result:
    print("Search Results:", result)
else:
    print("No results or an error occurred.")


top_gainers = api.get_top_gainers()
if top_gainers:
    for i, gainer in enumerate(top_gainers, 1):
        ticker = gainer.get("name", "Unknown Name")
        change = gainer.get("changesPercentage", "Unknown Change")
        print(f"{i}. {ticker}: {change}%")
else:
    print("No data found or an error occurred.")  
'''

top_losers = api.get_top_losers()
if top_losers:
    print("Top 5 Least Growth (Top Losers):")
    for i, loser in enumerate(top_losers, 1):
        name = loser.get("name", loser.get("symbol", "Unknown Name"))
        change = loser.get("changesPercentage", "Unknown Change")
        print(f"{i}. {name}: {change}%")
else:
    print("No data found or an error occurred.")