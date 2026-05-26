import yfinance as yf
t = yf.Ticker("AAPL")
print(t.news[:1])
