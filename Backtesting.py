import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt

from BuySellSignals import generate_dataframes, generate_signals, profit, leveraged_profit
from Indicator import generate_signals_indicator, calculate_indicator
from PerformanceMetrics import performance

#----------------------------------------------------#
#                   Data set-up                      #
#----------------------------------------------------#

# results from equity pair screening
data = {
    'Ticker 1': ['MLM', 'IBM', 'KLAC', 'ETN', 'ADI', 'IEX', 'LH', 'AMGN', 'CTAS', 'IBM', 'STZ', 'NSC', 'DOV', 'ANET', 'AME', 'NDSN', 'DHR', 'LIN', 'CTAS', 'DRI'],
    'Ticker 2': ['PH', 'VRSN', 'NDSN', 'JBL', 'ODFL', 'MSCI', 'QCOM', 'RSG', 'MOH', 'SYK', 'HUBB', 'ZBRA', 'MSFT', 'GWW', 'TSCO', 'TMUS', 'SHW', 'WMT', 'PGR', 'HON'],
    'Ratio Variance': [0.005718, 0.005133, 0.004253, 0.004090, 0.003839, 0.003498, 0.003237, 0.002821, 0.002727, 0.002554, 0.002547, 0.002400, 0.002009, 0.001832, 0.001695, 0.001329, 0.001023, 0.000782, 0.000750, 0.000740],
    'Cointegration Test P-Value': [0.026953, 0.003023, 0.000741, 0.011188, 0.001841, 0.018063, 0.004475, 0.024894, 0.015033, 0.018365, 0.016497, 0.005069, 0.017830, 0.013301, 0.015155, 0.007882, 0.027492, 0.026370, 0.014683, 0.024686],
    'Ranking': [191, 372, 288, 345, 136, 318, 204, 314, 146, 116, 390, 59, 85, 69, 322, 138, 22, 222, 364, 379]
}

ranked_df = pd.DataFrame(data)
df_list = generate_dataframes(ranked_df)

# results from commodities screening
selected_commodity = {
    'Ticker 1': ['PPLT', 'WEAT', 'CORN', 'CORN', 'CPER', 'WEAT', 'BCIM'],
    'Ticker 2': ['PALL', 'UNL', 'DBB', 'USL', 'SLV', 'DBB', 'DBB'],
    'Ratio Variance': [0.004637, 0.003130, 0.002529, 0.002384, 0.001787, 0.001783, 0.000063],
    'Cointegration Test P-Value': [0.120510, 0.007510, 0.153944, 0.111754, 0.212381, 0.069488, 0.054788],
    'Ranking': [34, 18, 8, 81, 1, 3, 64]
}

ranked_df_commodity = pd.DataFrame(selected_commodity)
df_list_commodity = generate_dataframes(ranked_df_commodity)

def plot_indicator_strategy(price_df, signals_df, indicator_lower_bound, indicator_upper_bound, show_one_year=True):
    fig, ax1 = plt.subplots()

    color = 'black'  # Change the color of the price ratio line to black
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price Ratio', color=color)
    ax1.plot(price_df.index, price_df['Raw Price Data 1'] / price_df['Raw Price Data 2'], color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim([price_df['Raw Price Data 1'].min() / price_df['Raw Price Data 2'].max(), price_df['Raw Price Data 1'].max() / price_df['Raw Price Data 2'].min()])  # Adjust y-axis limits

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Indicator', color=color)
    ax2.plot(signals_df.index, signals_df['Indicator'], color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    ax2.axhline(y=indicator_lower_bound, color='gray', linestyle='--')
    ax2.axhline(y=indicator_upper_bound, color='gray', linestyle='--')

    for index, row in signals_df.iterrows():
        if row['orders_ticker1'] == 1:
            ax1.scatter(index, price_df.loc[index, 'Raw Price Data 1'] / price_df.loc[index, 'Raw Price Data 2'], color='green', marker='^')
        elif row['orders_ticker2'] == 1:
            ax1.scatter(index, price_df.loc[index, 'Raw Price Data 1'] / price_df.loc[index, 'Raw Price Data 2'], color='red', marker='v')

    if show_one_year:
        ax1.set_xlim(pd.Timestamp('2023-01-01'), pd.Timestamp('2024-01-01'))

    fig.tight_layout()
    plt.title(f"{price_df['Ticker 1'].iloc[0]}/{price_df['Ticker 2'].iloc[0]} Indicator Strategy")
    plt.show()

# df = df_list[1]
# signals, paired_trades = generate_signals_indicator(df, 40, 60, 50)
# profit = profit(paired_trades, df)
# plot_indicator_strategy(df, signals, 40, 60)
#----------------------------------------------------#
# Run strategy function:                             #
#                                                    #
#  build a backtest portfolio based on various       #
#  conditions :                                      #
#                                                    #
#  Note: the user can choose between using the       #
#  initial strategy developed, which involves        #
#  opening a short or long position on the ratio     #
#  based on the extremeness of its current value     #
#  with respect to the moving average window. The    #
#  second option is to use the indicator strategy    #
#  which triggers signals based on the indicator     #
#  developed in Indicator.py                         #
#----------------------------------------------------#
#----------------------------------------------------#
#  ma: moving average/look-back window               #
#  use_leverage: boolean, if leveraged or not        #
#  leverage_ratio: leverage multiplier               #
#  use_initial_z_score: boolean, use z-score         #
#                       strategy                     #
#  z_value: critical z-score for buy/sell trigger    #
#  use_indicator_strategy: boolean, use indicator    #
#                          strategy                  #
#  lower_bound: indicator cutoff for long/buy        #
#               position on ratio                    #
#  upper_bound: indicator cutoff for short/sell      #
#               position on ratio                    #
#----------------------------------------------------#

def run_strategy(ma, df_list, use_leverage=False, leverage_ratio=False, use_initial_z_score=False, z_value=None,
                 use_indicator_strategy=False, lower_bound=None, upper_bound=None):

    all_dates = pd.date_range(start='2017-01-01', end='2024-01-01', freq='B')  # Assuming business days
    portfolio_data = pd.DataFrame({'Date': all_dates, 'Daily_Return': np.zeros(len(all_dates))})

    for idx, df in enumerate(df_list):
        if use_initial_z_score:
            signals_df, paired_trades = generate_signals(df, z_value, ma)
        elif use_indicator_strategy:
            signals_df, paired_trades = generate_signals_indicator(df, lower_bound, upper_bound, ma)
        else:
            raise ValueError("Please choose either initial z-score strategy or indicator strategy.")

        if paired_trades.empty:
            continue

        if use_leverage:
            profit_df = leveraged_profit(profit(paired_trades, df), leverage_ratio)
        else:
            profit_df = profit(paired_trades, df)

        if profit_df.empty:
            continue

        for index, row in portfolio_data.iterrows():
            date2_entry = row['Date']
            date2_entry = pd.to_datetime(date2_entry, format='%Y-%m-%d').strftime('%Y-%m-%d')
            profit_df['Date2'] = pd.to_datetime(profit_df['Date2'], format='%m-%d-%Y')
            matching_rows = profit_df[profit_df['Date2'].dt.strftime('%Y-%m-%d') == date2_entry]

            for _, matching_row in matching_rows.iterrows():
                portfolio_data.at[index, 'Daily_Return'] += matching_row['Pair_Profit']

    portfolio_data['Daily_Return'] /= len(df_list)
    portfolio_data = portfolio_data.dropna()
    portfolio_data['Cumulative_Return'] = (1 + portfolio_data['Daily_Return']).cumprod()

    return portfolio_data
#----------------------------------------------------#
#               Plotting Functions                   #
#----------------------------------------------------#
def plot_portfolio_value(portfolio_df):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot Cumulative_Return of the portfolio
    ax.plot(portfolio_df['Date'], portfolio_df['Cumulative_Return'], label='Portfolio', color='blue')
    sp500_data = yf.download('^GSPC', start='2017-01-01', end='2024-01-01')
    sp500_returns = sp500_data['Adj Close'].pct_change().dropna()
    sp500_cumulative = (1 + sp500_returns).cumprod()

    ax.plot(sp500_cumulative.index, sp500_cumulative, label='S&P 500', color='black', linestyle='--')

    ax.set_title('Portfolio vs S&P 500 Cumulative Returns')
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Returns')
    ax.legend()
    plt.show()

#----------------------------------------------------#
#                  Strategy Test                     #
#----------------------------------------------------#

indicator_portfolio = run_strategy(50, df_list, use_indicator_strategy=True, lower_bound=45, upper_bound=55)
zscore_portfolio = run_strategy(50, df_list, use_initial_z_score=True, z_value = 1.5)

#----------------------------------------------------#
#          Printing Performance of Backtest          #
#----------------------------------------------------#

performance(indicator_portfolio)
performance(zscore_portfolio)

#----------------------------------------------------#
#          Plotting Performance of Backtest          #
#----------------------------------------------------#

plot_portfolio_value(indicator_portfolio)
plot_portfolio_value(zscore_portfolio)

#----------------------------------------------------#
#               Parameter Optimization               #
#----------------------------------------------------#

# current method optimizes upperbound/lowerbound values for the indicator strategy
def optimize_params(df_list, optimize_for_sharpe=False, use_indicator_strategy=False):
    best_lower_bound = None
    best_upper_bound = None
    best_metric_value = float('-inf') if optimize_for_sharpe else float('-inf')
    best_z_score = None
    best_ma = None

    if use_indicator_strategy:
        lower_range = range(5, 35, 5)
        upper_range = range(30, 55, 5)  # Ensure upper_bound > lower_bound

        for lower_bound in lower_range:
            for upper_bound in upper_range:
                print(f"Testing Lower Bound: {lower_bound}, Upper Bound: {upper_bound}")

                # Run the strategy with the current lower bound and upper bound
                portfolio_df = run_strategy(50, df_list, use_indicator_strategy=True,
                                            lower_bound=lower_bound, upper_bound=upper_bound)

                # Calculate performance metrics
                performance_dict = performance(portfolio_df)

                # Extract the metric value (Sharpe ratio or CAGR) from the performance dictionary
                metric_value = float(performance_dict["Sharpe Ratio"]) if optimize_for_sharpe else float(
                    performance_dict["CAGR"])

                # Update best parameters if a higher metric value is found
                if metric_value > best_metric_value:
                    best_lower_bound = lower_bound
                    best_upper_bound = upper_bound
                    best_metric_value = metric_value

    else:
        z_score_range = [x * 0.2 + 0.3 for x in range(1, 12, 1)]
        ma_range = range(25, 200, 25)

        for z_score in z_score_range:
            for ma in ma_range:
                print(f"Testing Z-Score: {z_score}, Moving Average: {ma}")

                # Run the strategy with the current z-score and moving average
                portfolio_df = run_strategy(ma, df_list, use_initial_z_score=True, z_value=z_score)

                # Calculate performance metrics
                performance_dict = performance(portfolio_df)

                # Extract the metric value (Sharpe ratio or CAGR) from the performance dictionary
                metric_value = float(performance_dict["Sharpe Ratio"]) if optimize_for_sharpe else float(
                    performance_dict["CAGR"])

                # Update best parameters if a higher metric value is found
                if metric_value > best_metric_value:
                    best_z_score = z_score
                    best_ma = ma
                    best_metric_value = metric_value

    print("\nOptimization Result:")
    if use_indicator_strategy:
        print(f"Best Lower Bound: {best_lower_bound}")
        print(f"Best Upper Bound: {best_upper_bound}")
    else:
        print(f"Best Z-Score: {best_z_score}")
        print(f"Best Moving Average: {best_ma}")
    print(f"Best Metric Value: {best_metric_value}")

    return best_lower_bound, best_upper_bound if use_indicator_strategy else (best_z_score, best_ma)

# optimize_params(df_list, use_indicator_strategy=True)
# optimize_params(df_list, use_indicator_strategy=False)



