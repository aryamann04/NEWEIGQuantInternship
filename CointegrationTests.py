import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import coint
from PreSelectionTests import clean_price_data, pairs_measures, rank_pairs, ratio_var


def coint_test(pairs):
    cointegrated_pairs = []
    pairs_checked = 0

    for pair_num, (ticker1, ticker2) in pairs.items():
        try:
            # Clean data
            data_i, data_j = clean_price_data(ticker1, ticker2)

            # Perform cointegration test
            p_value = coint(data_i, data_j)[1]

            if p_value < 0.03:
                cointegrated_pairs.append((ticker1, ticker2, p_value, pair_num))
                pairs_checked += 1

            if pairs_checked >= 25:
                break

        except Exception as e:
            print(f"Error processing pair {ticker1} and {ticker2}: {e}")

    return cointegrated_pairs

def rank_var(pairs_data):
    # Create a DataFrame from the input data
    df = pd.DataFrame(pairs_data, columns=['Ticker 1', 'Ticker 2', 'Cointegration Test P-Value', 'Ranking'])

    df['Ratio Variance'] = df.apply(lambda row: ratio_var(row['Ticker 1'], row['Ticker 2']), axis=1)

    sorted_df = df.sort_values(by='Ratio Variance', ascending=False)
    sorted_df.reset_index(drop=True, inplace=True)

    return sorted_df[['Ticker 1', 'Ticker 2', 'Ratio Variance', 'Cointegration Test P-Value', 'Ranking']]