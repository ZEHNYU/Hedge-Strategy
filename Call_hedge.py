import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm

# Calculate Delta using the Black-Scholes model for call options
def calculate_call_delta(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        raise ValueError("Time to expiration (T) and volatility (sigma) must be positive")

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    delta = norm.cdf(d1)
    return delta

# Select out-of-the-money call options with strike <= 0.9 * S
def select_out_of_money_call_options(calls, S, percentage=0.9):
    sorted_calls = calls.sort_values(by='strike', ascending=True)
    filtered_calls = sorted_calls[sorted_calls['strike'] <= S * percentage]
    if len(filtered_calls) == 0:
        return sorted_calls.iloc[0]
    else:
        return filtered_calls.iloc[-1]

# Get options chain for a given ticker
def get_options_chain(ticker):
    try:
        asset = yf.Ticker(ticker)
        expiration_dates = asset.options
        if not expiration_dates:
            raise ValueError(f"No expiration dates available for {ticker} options.")
        options = asset.option_chain(expiration_dates[0])
        calls = options.calls
        return calls
    except Exception as e:
        print(f"Error fetching options chain for {ticker}: {e}")
        return pd.DataFrame()

# Main function for call options
def main_call(ticker):
    # Parameters
    portfolio_value = 1000000
    portfolio_volatility = 0.1137

    calls = get_options_chain(ticker)
    if calls.empty:
        print("Error: No call options data available.")
        return

    # Retrieve current price of the asset
    asset = yf.Ticker(ticker)
    S = asset.history(period="1d")['Close'].iloc[0]

    selected_call = select_out_of_money_call_options(calls, S, percentage=0.9)
    K = selected_call['strike']
    T = 1  # Time to expiration is 1 year
    r = 0.05
    sigma = selected_call['impliedVolatility']

    if sigma <= 0:
        print("Error: Implied volatility (sigma) is non-positive.")
        return

    try:
        delta = calculate_call_delta(S, K, T, r, sigma)
        contract_value = 100  # Typically, one stock option contract represents 100 shares
        required_contracts = portfolio_value * portfolio_volatility / (contract_value * delta)

        print(f'Strike Price: {K}')
        print(f'Call Options to Hedge: {required_contracts:.2f}')
    except Exception as e:
        print(f"Error in calculation: {e}")

if __name__ == '__main__':
    ticker = input("Enter the ticker symbol: ")
    main_call(ticker)