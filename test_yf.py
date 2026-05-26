import yfinance as yf
tickers = ["AAPL", "MSFT"]
data = yf.download(tickers, period="1y")
print(data.columns)
if 'Close' in data.columns:
    print("Has Close")
    print(data['Close'].head())
