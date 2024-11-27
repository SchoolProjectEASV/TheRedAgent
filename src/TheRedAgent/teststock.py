from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import logging

# Replace 'YOUR_API_KEY' with your actual Alpha Vantage API key
API_KEY = "N3J457GUET9DGQK2"

def get_top_stock_gainers():
    """Fetch the top 5 stock gainers based on percentage change."""
    try:
        ts = TimeSeries(key=API_KEY, output_format='pandas')
        
        # Fetch daily stock data for major indices or predefined stocks
        stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK.B", "JPM", "V"]  # Example stocks
        gainers = []

        for stock in stocks:
            data, meta_data = ts.get_daily(symbol=stock, outputsize='compact')
            latest_close = data['4. close'].iloc[0]
            previous_close = data['4. close'].iloc[1]
            percent_change = ((latest_close - previous_close) / previous_close) * 100
            gainers.append({
                "symbol": stock,
                "latest_close": latest_close,
                "percent_change": percent_change
            })

        # Sort by percentage change and select top 5 gainers
        top_gainers = sorted(gainers, key=lambda x: x["percent_change"], reverse=True)[:5]
        return top_gainers

    except Exception as e:
        logging.error(f"Error fetching stock gainers: {str(e)}")
        return [{"error": "Unable to fetch stock gainers at this time."}]

print(get_top_stock_gainers())
