# -*- coding: utf-8 -*-
"""
@author: AIT 582 Terch
"""


import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# List of tickers
tickers = ["TSLA", "AAPL", "GME", "AMC", "MSFT"]

# Download daily stock data for 2024
data = yf.download(tickers, start="2024-01-01", end="2025-01-01", group_by='ticker')

# Show first few rows for one ticker to verify
print(data['AAPL'].head())

# save each stock to a separate CSV
for ticker in tickers:
    df_ticker = data[ticker].copy()
    df_ticker = df_ticker.reset_index()
    df_ticker.to_csv(f"{ticker}_2024.csv", index=False)
 
    
plt.figure(figsize=(12, 6))

for ticker in tickers:
    plt.plot(data[ticker]['Close'], label=ticker)

plt.title("Stock Prices in 2024")
plt.xlabel("Date")
plt.ylabel("Close Price ($)")
plt.legend(title="Ticker")
plt.grid(True)
plt.tight_layout()
plt.show()