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

# Get VIX options chain
def get_vix_options_chain():
    vix = yf.Ticker('^VIX')
    expiration_dates = vix.options
    options = vix.option_chain(expiration_dates[0])
    calls = options.calls
    return calls

# Main function for call options
def main_call():
    # Parameters
    portfolio_value = 1000000 #<---import your portfolio value
    portfolio_volatility = 0.1137 #<---import your portfolio stdev

    calls = get_vix_options_chain()
    S = 12.29  # <-----VIX price please update yourself
    selected_call = select_out_of_money_call_options(calls, S, percentage=0.9) #<---select price*0.9 OTM call
    K = selected_call['strike'] #strike price
    T = 1
    r = 0.05
    sigma = selected_call['impliedVolatility']

    if sigma <= 0:
        print("Error: Implied volatility (sigma) is non-positive.")
        return

    delta = calculate_call_delta(S, K, T, r, sigma)
    contract_value = 100
    required_contracts = portfolio_value * portfolio_volatility / (contract_value * delta)

    print(f'Strike Price: {K}')
    print(f'Call Options to Hedge: {required_contracts}')

if __name__ == '__main__':
    main_call()