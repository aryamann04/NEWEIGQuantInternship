import pandas as pd
from matplotlib import pyplot as plt
from BuySellSignals import generate_dataframes, generate_signals, profit

data = {
    'Ticker 1': ['MLM', 'IBM', 'KLAC', 'ETN', 'ADI', 'IEX', 'LH', 'AMGN', 'CTAS', 'IBM', 'STZ', 'NSC', 'DOV', 'ANET', 'AME', 'NDSN', 'DHR', 'LIN', 'CTAS', 'DRI'],
    'Ticker 2': ['PH', 'VRSN', 'NDSN', 'JBL', 'ODFL', 'MSCI', 'QCOM', 'RSG', 'MOH', 'SYK', 'HUBB', 'ZBRA', 'MSFT', 'GWW', 'TSCO', 'TMUS', 'SHW', 'WMT', 'PGR', 'HON'],
    'Ratio Variance': [0.005718, 0.005133, 0.004253, 0.004090, 0.003839, 0.003498, 0.003237, 0.002821, 0.002727, 0.002554, 0.002547, 0.002400, 0.002009, 0.001832, 0.001695, 0.001329, 0.001023, 0.000782, 0.000750, 0.000740],
    'Cointegration Test P-Value': [0.026953, 0.003023, 0.000741, 0.011188, 0.001841, 0.018063, 0.004475, 0.024894, 0.015033, 0.018365, 0.016497, 0.005069, 0.017830, 0.013301, 0.015155, 0.007882, 0.027492, 0.026370, 0.014683, 0.024686],
    'Ranking': [191, 372, 288, 345, 136, 318, 204, 314, 146, 116, 390, 59, 85, 69, 322, 138, 22, 222, 364, 379]
}
#strategy parameters
z = 1.5
ma = 50
#index of pair in data to plot
n = 1

ranked_df = pd.DataFrame(data)
df = generate_dataframes(ranked_df)
signals_df, paired_trades = generate_signals(df[n], z, ma) #Corresponding to ANET/GWW
profit_df = profit(paired_trades, df[n])

def plot_cumulative_return(profit_df, df, z, ma):

    ticker1_name = df['Ticker 1'].iloc[-1]
    ticker2_name = df['Ticker 2'].iloc[-1]

    profit_df['Date1'] = pd.to_datetime(profit_df['Date1'])
    profit_df['Date2'] = pd.to_datetime(profit_df['Date2'])

    plt.figure(figsize=(12, 6))
    plt.plot(profit_df['Date2'], profit_df['Cumulative_Return'], label='Cumulative Return', color='black')

    min_return = profit_df['Cumulative_Return'].min()
    min_return_index = profit_df['Cumulative_Return'].idxmin()
    min_return_date = profit_df['Date2'].loc[min_return_index]

    end_return = profit_df['Cumulative_Return'].iloc[-1]

    plt.text(min_return_date, min_return, f'{min_return:.4f}', verticalalignment='bottom', color='red')
    plt.text(profit_df['Date2'].iloc[-1], end_return, f'{end_return:.4f}', verticalalignment='bottom', color='blue')

    plt.title(f"Cumulative Return for 1.0 Units Invested In {ticker1_name}/{ticker2_name} (with z = {z} and ma = {ma})")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.legend()
    plt.show()

def plot_ratio(signals_df, df, z, ma):

    ticker1_name = df['Ticker 1'].iloc[-1]
    ticker2_name = df['Ticker 2'].iloc[-1]

    plt.figure(figsize=(12, 6))
    plt.plot(signals_df.index, signals_df['Ratio standardized'], label=f'{ma}-day Standardized Price Ratio', color='black')
    plt.axhline(y=z, color='r', linestyle='--', label=f'Upper Critical Value ({z})')
    plt.axhline(y=-z, color='g', linestyle='--', label=f'Lower Critical Value ({-z})')

    buy_signals = signals_df[signals_df['orders_ticker1'] == 1]
    sell_signals = signals_df[signals_df['orders_ticker1'] == -1]

    plt.scatter(buy_signals.index, buy_signals['Ratio standardized'], marker='^', color='g', label='Buy Signal')
    plt.scatter(sell_signals.index, sell_signals['Ratio standardized'], marker='v', color='r', label='Sell Signal')

    plt.title(f"Ratio Z-Score and Critical Values for {ticker1_name}/{ticker2_name}")
    plt.xlabel("Date")
    plt.ylabel("Ratio Z-Score")
    plt.legend()
    plt.grid(True)
    plt.show()

plot_cumulative_return(profit_df, df[n], z, ma)
plot_ratio(signals_df, df[n], z, ma)

