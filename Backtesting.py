import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from BuySellSignals import generate_dataframes, generate_signals, profit
from CointegrationTests import rank_var
import datetime

results = [('AMGN', 'AAPL', 0.002674, 76)]
ranked_df = rank_var(results)
df_example = generate_dataframes(ranked_df)[0]

def plot_strategy(df_example, signals_df, profit_df):

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(df_example['Raw Price Data 1'].index, df_example['Raw Price Data 1'].values, label='Price Data', linewidth=2)

    ax.scatter(signals_df.index[signals_df['orders'] == 1],
               df_example['Raw Price Data 1'][signals_df['orders'] == 1],
               marker='^', color='g', label='Buy Signal')

    ax.scatter(signals_df.index[signals_df['orders'] == -1],
               df_example['Raw Price Data 1'][signals_df['orders'] == -1],
               marker='v', color='r', label='Sell Signal')

    ax.set_title('Trading Strategy with Buy/Sell Signals', fontsize=18)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()

    ax2 = ax.twinx()
    ax2.plot(profit_df.index, profit_df['Cumulative Returns'], label='Cumulative Returns', color='b', linestyle='--')
    ax2.plot(profit_df.index, profit_df['Normalized Returns'], label='Normalized Returns', color='r', linestyle='--')
    ax2.set_ylabel('Returns', color='b')
    ax2.tick_params(axis='y', labelcolor='b')

    return ax, fig




#=========================================================================#
#Printing Results#
#=========================================================================#



#=========================================================================#
#Plotting Results#
#=========================================================================#

signals, pairs = generate_signals(df_example)
ratios = signals['Ratio standardized']
fig, ax = plt.subplots(figsize=(12, 8))

ax.plot(ratios.index, ratios, label="Z-Score", color='black')
ax.scatter(signals.index[signals['orders_ticker1'] == 1], ratios[signals['orders_ticker1'] == 1], marker='^', color='green', label='Buy Signal')
ax.scatter(signals.index[signals['orders_ticker1'] == -1], ratios[signals['orders_ticker1'] == -1], marker='v', color='red', label='Sell Signal')

ax.axhline(1.5, color="green", linestyle='--', label="Upper Threshold (1.5)")
ax.axhline(-1.5, color="red", linestyle='--', label="Lower Threshold (-1.5)")
ax.axhline(0, color="black", linestyle='--', label="Mean")

ax.set_title('AMGN/AAPL: Price Ratio Z-Score', fontsize=18)
ax.set_xlabel('Date')
ax.set_ylabel('Price Ratio Z-Score')

start_date = datetime.datetime(2022, 1, 1)
end_date = datetime.datetime(2023, 1, 1)

ax.set_xlim(start_date, end_date)

ax.legend()
plt.tight_layout()

fig, ax2 = plt.subplots(figsize=(12, 8))
buy_signals1 = signals[signals['orders_ticker1'] == 1]
sell_signals1 = signals[signals['orders_ticker1'] == -1]
ax2.plot(df_example.index, df_example['Raw Price Data 1'], label='AMGN', color='black')
ax2.set_ylabel('Price', color='black')
ax2.tick_params('y', colors='black')
ax2.scatter(buy_signals1.index, df_example['Raw Price Data 1'].loc[buy_signals1.index], color='green', marker='^', label='Buy Signal')
ax2.scatter(sell_signals1.index, df_example['Raw Price Data 1'].loc[sell_signals1.index], color='red', marker='v', label='Sell Signal')
ax2.legend(loc='upper left')
ax2.set_xlim(start_date, end_date)
ax2.set_ylim(215, 295)
ax2.set_title('AMGN: Price and Signals, 2022', fontsize=18)

plt.tight_layout()


fig, ax3 = plt.subplots(figsize=(12, 8))
buy_signals2 = signals[signals['orders_ticker2'] == 1]
sell_signals2 = signals[signals['orders_ticker2'] == -1]
ax3.plot(df_example.index, df_example['Raw Price Data 2'], label='AAPL', color='black')
ax3.set_ylabel('Price', color='black')
ax3.tick_params('y', colors='black')
ax3.scatter(buy_signals2.index, df_example['Raw Price Data 2'].loc[buy_signals2.index], color='green', marker='^', label='Buy Signal')
ax3.scatter(sell_signals2.index, df_example['Raw Price Data 2'].loc[sell_signals2.index], color='red', marker='v', label='Sell Signal')
ax3.legend(loc='upper left')
ax3.set_xlim(start_date, end_date)
ax3.set_ylim(125,190)
ax3.set_title('AAPL: Price and Signals, 2022', fontsize=18)

plt.tight_layout()

plt.show()