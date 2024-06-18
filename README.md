# Cointegrated Equity Pairs Trading

## Overview

This project, completed during my internship at New England Investment Consulting Group, focuses on implementing a cointegrated pairs trading strategy using historical data of S&P 500 constituents. The goal is to identify pairs of securities that exhibit a cointegrated relationship and use this relationship to generate profitable trading signals. The strategy leverages the mean-reverting nature of cointegrated pairs to execute long and short positions based on the divergence and convergence of their price movements. 

The project tests the strategy using both the traditional z-score method as well as a novel indicator I created which factors in Relative Strength Index values. Further explanation is given below. The key of this strategy is that it is market-neutral, signified by the market beta values close to 0, and in fact performs best duing market downturns. With a low standard deviation and variance of returns, the strategy is best implemented with leverage in order to outperform the market with a strong risk-return profile. 

## Repository Structure 

- ```InitialScreening.py``` Queries Wikipedia to find current S&P 500 index constituents and filters them by basic fundamental criteria such as market capitalization, trailing EPS, and P/E ratio to find stable, large companies.
  
- ```PreselectionTests.py``` Tests and ranks all possible pairs of tickers returned by the initial screening by 7 criteria outlined by Brunetti & DeLuca (2023). These measures include the sum of squared deviations of log prices, the price ratio of log prices, correlation and covariances of the returns and log prices, and magnitude squared coherence.
  
- ```CointegrationTests.py``` Runs an Engel-Granger test of cointegration of the securities starting with the first ranked security pair and moving down ranks. When a pair exhibits strong cointegration (p<0.03), the pair is appended to a list. The first 25 pairs which satisfy this criteria are then ranked by the variance of their price ratio. The 20 pairs with the highest variance are chosen to trade.
  
- ```BuySellSignals.py``` Determines buy and sell signals via 2 methods. The classic method uses the 'extremeness' of the current price ratio of the two securities relative to a rolling mean. This is done by calculating a z-score, and if the z-score is above (below) a certain critical cutoff, then the ratio is deemed to be over (under) priced. For instance, if we have security A and security B, with a price ratio of p(A)/p(B), if the z-score is abnormally high, then we would sell A and buy B. If the z-score is abnormally low, then the ratio is cheap so we would buy A and sell B.
  
- ```Indicator.py``` Creates a novel way (the second method) to trade pairs. In addition to the z-score of the price ratio between the two securities, the signed difference between the RSI (Relative Strength Index) values of the two securities is used as another way to determine the relative price of the securities. For instance, if A has an RSI of 90 and and B has an RSI of 10, then the difference RSI(A) - RSI(B) would be 80 and would signify that the pair has a large difference in value. The indicator maps this information to the interval [0, 100] with 0 signifying a very cheap ratio and 100 an expensive ratio. Trading with this indicator improves the risk-return profile of the strategy significantly.
  
- ```PerformanceMetrics.py``` Contains methods to calculate essential performance metrics of the portfolio including compounded annual growth rate, Sharpe ratio, standard deviation, variance, Value-at-Risk, conditional Value-at-Risk, and Beta.
  
- ```Backtesting.py``` Contains methods to calculate profit and plot returns. The dynamic framework and the development of the data process allows various asset classes, including cryptocurrencies and commodities in addition to equities, to be backtested with this pairs trading algorithm. 

## Results 

### Z-Score Strategy (unleveraged): 
With a critical z-score of 1.1 and a look-back moving average window of 175 days, the strategy achieved a return of ***7.63%***, a market beta of ***0.00324***, and a Sharpe ratio of ***0.490***. The daily 95% VaR and cVaR achieved are ***-0.28%*** and ***-0.65%***. 
### Indicator Strategy (unleveraged): 
With a lower bound of 40 and upper bound of 52 and a look-back moving average window of 150 days, the strategy achieved a return of ***8.21%***, a market beta of ***0.00306***, and a Sharpe ratio of ***0.759***. The daily 95% VaR and cVaR achieved are ***-0.27%*** and ***-0.61%***. 

## View Reports 
01/30/2024: 
[Initial Proposal](https://github.com/aryamann04/NEWEIGQuantInternship/files/14254910/Quant.Initial.Proposal.pdf)

04/02/2024: 
[Latest Report](https://github.com/aryamann04/NEWEIGQuantInternship/files/14887638/Week.7.Report.pptx.pdf)

A special thank you to the Quantitative Research team at New England Investment Consulting Group for giving me guidance and advice through the development of this project. 
