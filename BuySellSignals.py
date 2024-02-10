import numpy as np
import pandas as pd
import yfinance as yf
from PreSelectionTests import clean_price_data

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

def generate_signals(df, z, ma):

    ticker1_ts = df['Raw Price Data 1']
    ticker2_ts = df['Raw Price Data 2']

    ratios = ticker1_ts / ticker2_ts
    ratios_mean = ratios.rolling(window=ma, min_periods=1, center=False).mean()
    ratios_std = ratios.rolling(window=ma, min_periods=1, center=False).std()
    z_scores = (ratios - ratios_mean) / ratios_std
    ratio_std = z_scores.copy()

    z_scores = np.where(z_scores > z, 1, np.where(z_scores < -1*z, -1, 0))

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


#results from screening and pre-selection/cointegration tests
data = {
    'Ticker 1': ['CEG', 'IBM', 'KLAC', 'ETN', 'ADI', 'IEX', 'LH', 'AMGN', 'CTAS', 'IBM', 'STZ', 'NSC', 'DOV', 'ANET', 'AME', 'NDSN', 'DHR', 'LIN', 'CTAS', 'DRI'],
    'Ticker 2': ['MAA', 'VRSN', 'NDSN', 'JBL', 'ODFL', 'MSCI', 'QCOM', 'RSG', 'MOH', 'SYK', 'HUBB', 'ZBRA', 'MSFT', 'GWW', 'TSCO', 'TMUS', 'SHW', 'WMT', 'PGR', 'HON'],
    'Ratio Variance': [0.005718, 0.005133, 0.004253, 0.004090, 0.003839, 0.003498, 0.003237, 0.002821, 0.002727, 0.002554, 0.002547, 0.002400, 0.002009, 0.001832, 0.001695, 0.001329, 0.001023, 0.000782, 0.000750, 0.000740],
    'Cointegration Test P-Value': [0.026953, 0.003023, 0.000741, 0.011188, 0.001841, 0.018063, 0.004475, 0.024894, 0.015033, 0.018365, 0.016497, 0.005069, 0.017830, 0.013301, 0.015155, 0.007882, 0.027492, 0.026370, 0.014683, 0.024686],
    'Ranking': [191, 372, 288, 345, 136, 318, 204, 314, 146, 116, 390, 59, 85, 69, 322, 138, 22, 222, 364, 379]
}

ranked_df = pd.DataFrame(data)
df = generate_dataframes(ranked_df)
total = 0
z = 1.1
ma = 200
print("critical_z = ", z)
print("ma = ", ma)
for idx, df in enumerate(df):

    signals_df, paired_trades = generate_signals(df, z, ma)
    profit_df = profit(paired_trades, df)

    ticker1_name = df['Ticker 1'].iloc[0]
    ticker2_name = df['Ticker 2'].iloc[0]

    percent = (profit_df['Cumulative_Return'].iloc[-1] - 1)*100
    total += percent

    print(f"{idx + 1}  {ticker1_name}/{ticker2_name}: {percent:.2f}% ({((percent/100 + 1) ** (1/7) - 1) * 100:.2f}%)")

print("*"*50)
print(f"Average Return Across 20 Holdings: {total/20:.2f}%")
print(f"CAGR: {(((total/20)/100 + 1) ** (1/7) - 1) * 100:.2f}%")





