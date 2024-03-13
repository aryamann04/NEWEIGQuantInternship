import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt

from BuySellSignals import generate_dataframes, generate_signals, profit, leveraged_profit
from Indicator import generate_signals_indicator
from PerformanceMetrics import performance, get_sp500_returns

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

# results from leveraged etf screening
selected_leveraged_etfs = {
    'Ticker 1': ['UGL', 'QTJA', 'IWML', 'SCDL', 'USML', 'UPW', 'IWDL', 'IWDL', 'SCDL', 'BDCX', 'IWDL', 'SCDL', 'YCL', 'SCDL', 'IWDL', 'SCDL', 'IWML', 'OOTO', 'IWML', 'IWML', 'TSLR', 'XNOV', 'IWFL', 'YCS', 'XNOV'],
    'Ticker 2': ['BRZU', 'UVIX', 'CLDL', 'UBOT', 'SKYU', 'EDC', 'MVRL', 'OOTO', 'IWML', 'TPOR', 'YCS', 'AGQ', 'LABU', 'HDLB', 'YCL', 'BIB', 'UBT', 'EFO', 'UJB', 'MVV', 'XOCT', 'MIDU', 'TSLT', 'XNOV', 'XSEP'],
    'Ratio Variance': [4.158846e-02, 4.023644e-02, 3.394557e-02, 2.900719e-02, 2.761149e-02, 2.093654e-02, 1.086024e-02, 1.030949e-02, 6.830283e-03, 5.698188e-03, 4.990621e-03, 4.928351e-03, 4.674838e-03, 4.496338e-03, 3.381513e-03, 2.444474e-03, 1.926844e-03, 1.793360e-03, 1.646905e-03, 1.295539e-03, 8.186826e-04, 5.823167e-04, 3.697803e-04, 1.679705e-04, 5.175549e-08],
    'Cointegration Test P-Value': [0.008838, 0.005535, 0.021283, 0.013456, 0.029612, 0.025566, 0.022467, 0.013931, 0.007788, 0.006544, 0.008969, 0.015294, 0.015965, 0.011691, 0.008482, 0.011781, 0.009071, 0.013513, 0.006073, 0.013454, 0.002283, 0.007315, 0.004888, 0.000045, 0.013690],
    'Ranking': [229, 167, 45, 410, 122, 400, 147, 13, 313, 112, 37, 81, 70, 46, 370, 177, 351, 380, 226, 76, 18, 30, 206, 372, 352]
}

ranked_df = pd.DataFrame(data)
df_list = generate_dataframes(ranked_df)

ranked_df_etf = pd.DataFrame(selected_leveraged_etfs)
df_list_etf = generate_dataframes(ranked_df_etf)


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

indicator_portfolio = run_strategy(50, df_list, use_indicator_strategy=True, lower_bound=10, upper_bound=40)
zscore_portfolio = run_strategy(50, df_list, use_initial_z_score=True, z_value = 1.5)

indicator_portfolio_leveraged_etf = run_strategy(50, df_list_etf, use_indicator_strategy=True, lower_bound=10, upper_bound=40)
zscore_portfolio_leveraged_etf = run_strategy(50, df_list_etf, use_initial_z_score=True, z_value = 1.5)

indicator_portfolio_leveraged = run_strategy(50, df_list, use_leverage=True, leverage_ratio=3, use_indicator_strategy=True, lower_bound=10, upper_bound=40)
zscore_portfolio_leveraged = run_strategy(50, df_list, use_leverage= True, leverage_ratio=3, use_initial_z_score=True, z_value=1.5)

#----------------------------------------------------#
#          Printing Performance of Backtest          #
#----------------------------------------------------#

performance(indicator_portfolio)
performance(zscore_portfolio)

performance(indicator_portfolio_leveraged_etf)
performance(zscore_portfolio_leveraged_etf)

performance(indicator_portfolio_leveraged)
performance(zscore_portfolio_leveraged)

#----------------------------------------------------#
#          Plotting Performance of Backtest          #
#----------------------------------------------------#

plot_portfolio_value(indicator_portfolio)
plot_portfolio_value(zscore_portfolio)

plot_portfolio_value(indicator_portfolio_leveraged_etf)
plot_portfolio_value(zscore_portfolio_leveraged_etf)

plot_portfolio_value(indicator_portfolio_leveraged)
plot_portfolio_value(zscore_portfolio_leveraged)
