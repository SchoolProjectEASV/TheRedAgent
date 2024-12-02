from FinAPIWrapper import FinancialModelingPrepAPI

# Replace before push
api = FinancialModelingPrepAPI(api_key="Random")

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
        print(f"{i}. {gainer['name']}: {gainer['changesPercentage']}%")
else:
    print("No data found or an error occurred.")