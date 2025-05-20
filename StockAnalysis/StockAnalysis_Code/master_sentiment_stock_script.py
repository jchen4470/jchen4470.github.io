# -*- coding: utf-8 -*-
"""
Reddit Sentiment + Stock Price Correlation Script
Created for AIT 582 by Abdul
"""

import os
import pandas as pd
import numpy as np
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

# Ensure NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

# Set working directory to wherever your files are
data_dir = r'C:\Users\babdu\Documents\Mason\Masters\AIT 582\ProjectData'

# --- Load Reddit CSV ---
reddit_csv_path = os.path.join(data_dir, 'wallstreetbets_2022.csv')
df = pd.read_csv(reddit_csv_path, usecols=['title', 'body', 'timestamp', 'score'])

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp'])
df = df[df['timestamp'].dt.year == 2024]  # Filter to 2024

# Clean text
df['title'] = df['title'].astype(str).str.strip().str.lower()
df_filtered = df[(df['title'] != 'comment') & (df['score'] > 50)]
df_filtered = df_filtered.dropna(subset=['body', 'title'])

# Tokenization
tokenizer = RegexpTokenizer(r'\w+')
stop_words = set(stopwords.words('english'))
def tokenize_text(text):
    return [word for word in tokenizer.tokenize(text.lower()) if word not in stop_words]

df_filtered['title_tokens'] = df_filtered['title'].apply(tokenize_text)
df_filtered['body_tokens'] = df_filtered['body'].apply(tokenize_text)
df_filtered['title_cleaned'] = df_filtered['title_tokens'].apply(lambda x: ' '.join(x))
df_filtered['body_cleaned'] = df_filtered['body_tokens'].apply(lambda x: ' '.join(x))

# Sentiment Analysis
sia = SentimentIntensityAnalyzer()
df_filtered['sentiment_score'] = df_filtered['body_cleaned'].apply(lambda x: sia.polarity_scores(x)['compound'])

# Group by date
reddit_sentiment = df_filtered.groupby(df_filtered['timestamp'].dt.date)['sentiment_score'].mean()
reddit_sentiment.index = pd.to_datetime(reddit_sentiment.index)
reddit_sentiment = reddit_sentiment.to_frame(name='Reddit_Sentiment')

# --- Load Stock Price Data ---
stock_files = {
    'AAPL': os.path.join(data_dir, 'AAPL_2024.csv'),
    'AMC': os.path.join(data_dir, 'AMC_2024.csv'),
    'GME': os.path.join(data_dir, 'GME_2024.csv'),
    'MSFT': os.path.join(data_dir, 'MSFT_2024.csv'),
    'TSLA': os.path.join(data_dir, 'TSLA_2024.csv')
}

stock_data = {}
for ticker, path in stock_files.items():
    df_stock = pd.read_csv(path)
    df_stock['Date'] = pd.to_datetime(df_stock['Date'])
    df_stock = df_stock[['Date', 'Close']].rename(columns={'Close': f'{ticker}_Close'})
    stock_data[ticker] = df_stock.set_index('Date')

combined_stock_data = pd.concat(stock_data.values(), axis=1, join='outer').sort_index()

# Merge sentiment and stock data
combined_df = pd.concat([reddit_sentiment, combined_stock_data], axis=1, join='inner')

# --- Plotting ---
for ticker in stock_files.keys():
    plt.figure(figsize=(12, 6))
    ax1 = combined_df['Reddit_Sentiment'].plot(label='Reddit Sentiment', color='blue', legend=True)
    ax2 = combined_df[f'{ticker}_Close'].plot(secondary_y=True, label=f'{ticker} Close Price', color='red', legend=True)
    plt.title(f'{ticker} Stock Price vs Reddit Sentiment (2024)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --- Correlation ---
correlations = {}
for ticker in stock_files.keys():
    sentiment = combined_df['Reddit_Sentiment']
    prices = combined_df[f'{ticker}_Close']
    valid = sentiment.notna() & prices.notna()
    if valid.sum() > 0:
        corr, pval = stats.pearsonr(sentiment[valid], prices[valid])
        correlations[ticker] = {'Pearson Correlation': round(corr, 4), 'P-value': round(pval, 4)}

correlation_df = pd.DataFrame(correlations).T
print("\nPearson Correlation Results:")
print(correlation_df)

# Export merged dataset
output_path = os.path.join(data_dir, 'Reddit_Sentiment_with_Stock_Prices.csv')
combined_df.to_csv(output_path)
print(f"\nExported merged data to: {output_path}")