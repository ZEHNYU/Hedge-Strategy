import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm

# Calculate Delta using the Black-Scholes model for put options
def calculate_put_delta(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        raise ValueError("Time to expiration (T) and volatility (sigma) must be positive")

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    delta = -norm.cdf(-d1)
    return delta

# Select out-of-the-money put option with strike >= 1.1 * S
def select_out_of_money_put_option(puts, S, percentage=1.1):
    target_strike = S * percentage
    puts = puts.dropna(subset=['strike', 'impliedVolatility'])
    closest_put = puts.iloc[(puts['strike'] - target_strike).abs().argsort()[:1]]
    return closest_put.iloc[0]

# Get options chain for a given ticker
def get_options_chain(ticker):
    try:
        asset = yf.Ticker(ticker)
        expiration_dates = asset.options
        if not expiration_dates:
            raise ValueError(f"No expiration dates available for {ticker} options.")
        options = asset.option_chain(expiration_dates[0])
        puts = options.puts
        return puts
    except Exception as e:
        print(f"Error fetching options chain for {ticker}: {e}")
        return pd.DataFrame()

# Main function for put options
def main_put(ticker):
    # Parameters
    portfolio_value = 1000000
    portfolio_volatility = 0.1137

    puts = get_options_chain(ticker)
    if puts.empty:
        print("Error: No put options data available.")
        return

    # Retrieve current price of the asset
    asset = yf.Ticker(ticker)
    S = asset.history(period="1d")['Close'].iloc[0]

    selected_put = select_out_of_money_put_option(puts, S, percentage=1.1)
    K = selected_put['strike']
    T = 1  # Time to expiration is 1 year
    r = 0.05
    sigma = selected_put['impliedVolatility']

    if sigma <= 0:
        print("Error: Implied volatility (sigma) is non-positive.")
        return

    try:
        delta = calculate_put_delta(S, K, T, r, sigma)
        contract_value = 100  # Typically, one stock option contract represents 100 shares
        required_contracts = portfolio_value * portfolio_volatility / (contract_value * abs(delta))

        print(f'Strike Price: {K}')
        print(f'Put Options to Hedge: {required_contracts:.2f}')
    except Exception as e:
        print(f"Error in calculation: {e}")

if __name__ == '__main__':
    ticker = input("Enter the ticker symbol: ")
    main_put(ticker)