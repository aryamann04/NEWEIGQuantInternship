import numpy as np
import pandas as pd
import yfinance as yf

def get_sp500_returns():
    sp500_data = yf.download('^GSPC', start='2017-01-01', end='2024-01-01')
    sp500_returns = sp500_data['Adj Close'].pct_change().dropna()
    return sp500_returns

def sharpe(portfolio_df):
    rf = 4.17
    portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])
    portfolio_df['Year'] = portfolio_df['Date'].dt.year
    annual_returns = portfolio_df.groupby('Year')['Cumulative_Return'].last().pct_change() * 100
    if 2017 in portfolio_df['Year'].unique():
         annual_returns.loc[2017] = (portfolio_df.loc[portfolio_df['Year'] == 2017, 'Cumulative_Return'].iloc[-1] - 1) * 100
    excess_returns = annual_returns - rf
    sharpe_ratio = excess_returns.mean() / excess_returns.std()

    return f"{sharpe_ratio:.3f}"

def variance(portfolio_df):
    portfolio_returns = portfolio_df['Daily_Return'].dropna()
    variance_value = portfolio_returns.var() * 252  # Annualizing variance

    return f"{variance_value:.3f}"

def var(portfolio_df):
    portfolio_returns = portfolio_df['Daily_Return'].dropna()
    var_value = np.percentile(portfolio_returns, 5) * 100  # Convert to percentage
    return f"{var_value:.2f}%"

def win_rate(portfolio_df):
    non_zero_returns_df = portfolio_df[portfolio_df['Daily_Return'] != 0]
    total_trades = len(non_zero_returns_df)
    winning_trades = len(non_zero_returns_df[non_zero_returns_df['Daily_Return'] > 0])
    win_rate_value = (winning_trades / total_trades) * 100
    win_rate_f = "{:.2f}%".format(win_rate_value)

    return win_rate_f

def cagr(portfolio_df):
    cagr_value = ((portfolio_df['Cumulative_Return'].iloc[-1]) ** (252 / len(portfolio_df['Cumulative_Return'])) - 1) * 100
    formatted_cagr = "{:.2f}%".format(cagr_value)

    return formatted_cagr

def performance(portfolio_df):

    performance_dict = {
        "Sharpe Ratio": sharpe(portfolio_df),
        "Variance": variance(portfolio_df),
        "Value at Risk (VaR)": var(portfolio_df),
        "Win Rate": win_rate(portfolio_df),
        "CAGR": cagr(portfolio_df)
    }

    print("\nPerformance Metrics:")
    for metric, value in performance_dict.items():
        print(f"{metric}: {value}")

    return performance_dict



