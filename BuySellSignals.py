import numpy as np
import pandas as pd
import yfinance as yf
from CointegrationTests import rank_var
from PreSelectionTests import clean_price_data

results = [('ADI', 'AZO', 0.002674, 76)]
ranked_df = rank_var(results)

# rank_var output as input
def generate_dataframes(df):
    dataframes = []

    for index, row in df.iterrows():
        ticker1, ticker2 = row['Ticker 1'], row['Ticker 2']
        data_i, data_j = clean_price_data(ticker1, ticker2)

        if data_i is not None and data_j is not None:

            price_ratio = data_i / data_j
            raw_price_data1 = yf.download(ticker1, start='2017-01-01', end='2024-01-01')['Close']
            raw_price_data2 = yf.download(ticker2, start='2017-01-01', end='2024-01-01')['Close']

            result_df = pd.DataFrame({
                'Ticker 1': [ticker1] * len(data_i),
                'Ticker 2': [ticker2] * len(data_j),
                'Date': data_i.index,
                'Raw Price Data 1': raw_price_data1,
                'Raw Price Data 2': raw_price_data2,
                'Cleaned Price Data 1': data_i.values,
                'Cleaned Price Data 2': data_j.values,
                'Price Ratio': price_ratio.values,
            })

            dataframes.append(result_df)

    return dataframes

def generate_signals(df_example):

    ticker1_ts = df_example['Raw Price Data 1']
    ticker2_ts = df_example['Raw Price Data 2']

    ratios = ticker1_ts / ticker2_ts
    ratios_mean = ratios.rolling(window=50, min_periods=1, center=False).mean()
    ratios_std = ratios.rolling(window=50, min_periods=1, center=False).std()
    z_scores = (ratios - ratios_mean) / ratios_std
    ratio_std = z_scores.copy()

    z_scores = np.where(z_scores > 1.5, 1, np.where(z_scores < -1.5, -1, 0))

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

        pairsdf = pd.DataFrame(pairs)

    return signals_df, pairsdf


def profit(trades_df, price_df):

    trades_df['Pair_Profit'] = 0.0
    trades_df['Cumulative_Return'] = 1.0

    for index, row in trades_df.iterrows():
        date1 = pd.to_datetime(row['Date1'], format='%m-%d-%Y')
        date2 = pd.to_datetime(row['Date2'], format='%m-%d-%Y')

        if (row['TradeType'] == 'Long'):
            buy = price_df.loc[date1, 'Raw Price Data 1']
            sell = price_df.loc[date2, 'Raw Price Data 1']
            short = price_df.loc[date1, 'Raw Price Data 2']
            cover = price_df.loc[date2, 'Raw Price Data 2']
        else:
            cover = price_df.loc[date1, 'Raw Price Data 1']
            short = price_df.loc[date2, 'Raw Price Data 1']
            buy = price_df.loc[date1, 'Raw Price Data 2']
            sell = price_df.loc[date2, 'Raw Price Data 2']

        pair_profit = (sell / buy - 1) + (short / cover - 1)
        trades_df.at[index, 'Pair_Profit'] = pair_profit
        cumulative_return = trades_df['Cumulative_Return'].iloc[index - 1] * (1 + pair_profit)
        trades_df.at[index, 'Cumulative_Return'] = cumulative_return

    return trades_df
pd.set_option('display.max_rows', None)  # Show all rows


df = generate_dataframes(ranked_df)[0]
signals_df, paired_trades = generate_signals(df)

profit = profit(paired_trades, df)
print(profit)





