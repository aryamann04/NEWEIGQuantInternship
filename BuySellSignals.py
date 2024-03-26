import numpy as np
import pandas as pd
import yfinance as yf

from PreSelectionTests import clean_price_data
pd.set_option('display.max_rows', None)

#----------------------------------------------------#
#  Method to generate price data for selected pairs  #
#----------------------------------------------------#
def generate_dataframes(df):
    dataframes = []

    for index, row in df.iterrows():
        ticker1, ticker2 = row['Ticker 1'], row['Ticker 2']
        data_i, data_j = clean_price_data(ticker1, ticker2)

        if data_i is not None and data_j is not None:

            raw_price_data1 = yf.download(ticker1, start='2017-01-01', end='2024-01-01')['Close']
            raw_price_data2 = yf.download(ticker2, start='2017-01-01', end='2024-01-01')['Close']

            common_dates = raw_price_data1.index.intersection(raw_price_data2.index)
            raw_price_data1 = raw_price_data1[common_dates]
            raw_price_data2 = raw_price_data2[common_dates]

            result_df = pd.DataFrame({
                'Ticker 1': [ticker1] * len(data_i),
                'Ticker 2': [ticker2] * len(data_j),
                'Date': raw_price_data1.index,
                'Raw Price Data 1': raw_price_data1,
                'Raw Price Data 2': raw_price_data2,
            })

            dataframes.append(result_df)

    return dataframes
#----------------------------------------------------#
# Generate signals based on initial z-score strategy:#
#                                                    #
#  sell if the ratio z-score crosses above a preset  #
#  value, buy if below                               #
#----------------------------------------------------#
def generate_signals(df, z, ma):
    ticker1_ts = df['Raw Price Data 1']
    ticker2_ts = df['Raw Price Data 2']

    ratios = ticker1_ts / ticker2_ts
    ratios_mean = ratios.rolling(window=ma, min_periods=1, center=False).mean()
    ratios_std = ratios.rolling(window=ma, min_periods=1, center=False).std()
    z_scores = (ratios - ratios_mean) / ratios_std
    ratio_std = z_scores.copy()

    z_scores = np.where(z_scores > z, 1, np.where(z_scores < -1 * z, -1, 0))

    signals_df = pd.DataFrame(index=ticker1_ts.index)
    signals_df['signal_ticker1'] = z_scores * -1
    signals_df['signal_ticker2'] = z_scores
    signals_df['Ratio standardized'] = ratio_std
    signals_df['orders_ticker1'] = signals_df['signal_ticker1'].diff()
    signals_df['orders_ticker2'] = signals_df['signal_ticker2'].diff()

    filtered = signals_df.loc[(signals_df['orders_ticker1'] != 0) & (signals_df['orders_ticker2'] != 0)]
    filtered = filtered.drop(columns=['signal_ticker1', 'signal_ticker2'])
    filtered['Holding Period'] = filtered.index.to_series().diff().dt.days
    filtered = filtered.iloc[1:]

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

#----------------------------------------------------#
#              Profit Calculation                    #
#----------------------------------------------------#
def profit(trades_df, price_df, fee=0.01):
    trades_df['Pair_Profit'] = 0.0
    trades_df['Cumulative_Return'] = 1.0
    position_b = 1
    for index, row in trades_df.iterrows():
        date1 = pd.to_datetime(row['Date1'], format='%m-%d-%Y')
        date2 = pd.to_datetime(row['Date2'], format='%m-%d-%Y')
        if row['TradeType'] == 'Long':
            buy_a = price_df.loc[date1, 'Raw Price Data 1']
            sell_a = price_df.loc[date2, 'Raw Price Data 1']
            short_b = price_df.loc[date1, 'Raw Price Data 2']
            cover_b = price_df.loc[date2, 'Raw Price Data 2']
            # position_b = buy_a / short_b
            pair_profit = ((sell_a / buy_a - 1) + (position_b * (1 - cover_b / short_b))) / 2
        else:
            short_a = price_df.loc[date1, 'Raw Price Data 1']
            cover_a = price_df.loc[date2, 'Raw Price Data 1']
            buy_b = price_df.loc[date1, 'Raw Price Data 2']
            sell_b = price_df.loc[date2, 'Raw Price Data 2']
            # position_b = short_a / buy_b
            pair_profit = ((position_b * (sell_b / buy_b) - 1) + (1 - cover_a / short_a)) / 2


        trades_df.at[index, 'Pair_Profit'] = pair_profit
        cumulative_return = trades_df['Cumulative_Return'].iloc[index - 1] * (1 + pair_profit)
        trades_df.at[index, 'Cumulative_Return'] = cumulative_return
        trades_df['Win Rate'] = np.where(trades_df['Pair_Profit'] > 0, 1, 0)

    return trades_df

def leveraged_profit(profit_df, leverage_ratio):

    leveraged_df = profit_df.copy()
    leveraged_df['Pair_Profit'] = leveraged_df['Pair_Profit'] * leverage_ratio
    leveraged_df['Cumulative_Return'] = (1 + leveraged_df['Pair_Profit']).cumprod()

    return leveraged_df


