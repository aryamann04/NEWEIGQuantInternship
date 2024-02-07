import bs4 as bs
import requests
import yfinance as yf

def get_sp500():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)

    tickers = [s.replace('\n', '') for s in tickers]
    return tickers

def screen(mkt_cap, eps, pe_low, pe_high):
    tickers = get_sp500()
    selected_companies = []

    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            market_cap = info.get('marketCap', None)
            trailing_eps = info.get('trailingEps', None)
            price_to_earnings = info.get('trailingPE', None)

            if (market_cap is not None and trailing_eps is not None
                    and price_to_earnings is not None):
                if (market_cap >= mkt_cap and trailing_eps >= eps
                        and pe_low <= price_to_earnings <= pe_high):
                    selected_companies.append(ticker)
        except Exception:
            pass

    return selected_companies