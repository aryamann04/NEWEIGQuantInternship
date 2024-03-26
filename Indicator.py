import numpy as np
import pandas as pd
import math

def calculate_rsi(prices, period):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.ewm(com=period - 1, min_periods=1).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_indicator(df, lookback_window):
    ticker1_prices = df['Raw Price Data 1']
    ticker2_prices = df['Raw Price Data 2']

    # Calculate ratio z-scores
    ratios = ticker1_prices / ticker2_prices
    ratios_mean = ratios.rolling(window=lookback_window, min_periods=1, center=False).mean()
    ratios_std = ratios.rolling(window=lookback_window, min_periods=1, center=False).std()
    z_scores = (ratios - ratios_mean) / ratios_std
    indicator_z_score = (1 / (1 + np.exp(-z_scores)))  # Normalize from 0 to 1

    # Calculate RSI difference for each ticker
    rsi_ticker1 = calculate_rsi(ticker1_prices, lookback_window)
    rsi_ticker2 = calculate_rsi(ticker2_prices, lookback_window)
    rsi_difference = (1 / (1 + np.exp(-1*(rsi_ticker1 - rsi_ticker2) / 10 )))  # Normalize RSI difference from 0 to 1

    combined_indicator = 100 * (0.5 * indicator_z_score + 0.5 * rsi_difference)

    return combined_indicator

def generate_signals_indicator(df, lower_bound, upper_bound, ma):

    indicator = calculate_indicator(df, ma)
    ticker1_ts = df['Raw Price Data 1']
    ticker2_ts = df['Raw Price Data 2']

    ratios = ticker1_ts / ticker2_ts
    ratios_mean = ratios.rolling(window=ma, min_periods=1, center=False).mean()
    ratios_std = ratios.rolling(window=ma, min_periods=1, center=False).std()
    z_scores = (ratios - ratios_mean) / ratios_std

    # Generate signals based on the indicator values
    signals_df = pd.DataFrame(index=df.index)
    signals_df['signal_ticker1'] = np.where(indicator < lower_bound, 1, np.where(indicator > upper_bound, -1, 0))
    signals_df['signal_ticker2'] = -signals_df['signal_ticker1']


    signals_df['Ratio standardized'] = z_scores
    signals_df['Indicator'] = indicator

    signals_df['orders_ticker1'] = signals_df['signal_ticker1'].diff()
    signals_df['orders_ticker2'] = signals_df['signal_ticker2'].diff()

    filtered = signals_df.loc[(signals_df['orders_ticker1'] != 0) & (signals_df['orders_ticker2'] != 0)]
    filtered = filtered.drop(columns=['signal_ticker1', 'signal_ticker2'])
    filtered['Holding Period'] = filtered.index.to_series().diff().dt.days
    filtered = filtered.iloc[1:]

    # Extract pairs information
    pairs = []

    for i in range(0, len(filtered) - 1, 2):
        row1 = filtered.iloc[i]
        row2 = filtered.iloc[i + 1]

        date1 = row1.name.strftime('%m-%d-%Y')
        date2 = row2.name.strftime('%m-%d-%Y')
        trade_type = 'Long' if row1['orders_ticker1'] == 1 else 'Short'
        holding_period = row2['Holding Period']

        pairs.append({
            'Date1': date1,
            'Date2': date2,
            'TradeType': trade_type,
            'Holding Period': holding_period
        })

    pairs_df = pd.DataFrame(pairs)

    return signals_df, pairs_df
