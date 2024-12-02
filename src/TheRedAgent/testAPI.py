from FinAPIWrapper import FinancialModelingPrepAPI

# Replace before push
api = FinancialModelingPrepAPI(api_key="random")

query = "Apple"
result = api.search_company(query)
if result:
    print("Search Results:", result)
else:
    print("No results or an error occurred.")
