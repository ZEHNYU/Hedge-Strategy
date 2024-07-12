import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm


def calculate_put_delta(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        raise ValueError("Time to expiration (T) and volatility (sigma) must be positive")
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    delta = -norm.cdf(-d1)
    return delta


def get_vix_options_chain():
    try:
        vix = yf.Ticker('^VIX')
        expiration_dates = vix.options
        if not expiration_dates:
            raise ValueError("No expiration dates available for VIX options.")
        options = vix.option_chain(expiration_dates[0])
        puts = options.puts
        return puts
    except Exception as e:
        print(f"Error fetching VIX options chain: {e}")
        return pd.DataFrame()


def calculate_hedging_cost(put_option, S, T, r, portfolio_value, portfolio_volatility):
    K = put_option['strike']
    sigma = put_option['impliedVolatility']
    option_price = put_option['lastPrice']

    if sigma <= 0:
        return float('inf')  # Return infinity for invalid options

    try:
        delta = calculate_put_delta(S, K, T, r, sigma)
        contract_value = 100
        required_contracts = portfolio_value * portfolio_volatility / (contract_value * abs(delta))
        total_cost = required_contracts * contract_value * option_price
        return total_cost, required_contracts, delta
    except:
        return float('inf'), 0, 0


def main_put():
    portfolio_value = 1000000
    portfolio_volatility = 0.1137
    S = 12.9  # VIX price
    T = 1  # date to maturity
    r = 0.05

    puts = get_vix_options_chain()
    if puts.empty:
        print("Error: No put options data available.")
        return

    min_cost = float('inf')
    min_cost_option = None
    min_cost_contracts = 0
    min_cost_delta = 0

    for _, put in puts.iterrows():
        cost, contracts, delta = calculate_hedging_cost(put, S, T, r, portfolio_value, portfolio_volatility)
        if cost < min_cost:
            min_cost = cost
            min_cost_option = put
            min_cost_contracts = contracts
            min_cost_delta = delta

    print("Minimum Cost Strategy:")
    if min_cost_option is not None:
        print(f'Strike Price: {min_cost_option["strike"]}')
        print(f'Put Options to Hedge: {min_cost_contracts:.2f}')
        print(f'Option Delta: {min_cost_delta:.4f}')
        print(f'Option Price: ${min_cost_option["lastPrice"]:.2f}')
        print(f'Total Cost: ${min_cost:.2f}')
        print(f'Moneyness: {min_cost_option["strike"] / S:.2%}')
    else:
        print("No valid options found for minimum cost strategy.")

    print('\n90% Strike Price Strategy:')
    target_strike = S * 0.9
    closest_put = puts.iloc[(puts['strike'] - target_strike).abs().argsort()[:1]].iloc[0]
    cost_90, contracts_90, delta_90 = calculate_hedging_cost(closest_put, S, T, r, portfolio_value,
                                                             portfolio_volatility)

    print(f'Strike Price: {closest_put["strike"]}')
    print(f'Put Options to Hedge: {contracts_90:.2f}')
    print(f'Option Delta: {delta_90:.4f}')
    print(f'Option Price: ${closest_put["lastPrice"]:.2f}')
    print(f'Total Cost: ${cost_90:.2f}')
    print(f'Moneyness: {closest_put["strike"] / S:.2%}')

    print("\nComparison:")
    print(f'Minimum Cost: ${min_cost:.2f}')
    print(f'90% Strategy Cost: ${cost_90:.2f}')
    print(f'Difference: ${cost_90 - min_cost:.2f}')

if __name__ == '__main__':
    main_put()