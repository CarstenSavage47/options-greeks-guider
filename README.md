# Options Helper App
The objective of this Dash app is to give you an intuitive interpretation of the greeks for a given option contract.

For example:
- How will implied volatility (vega) affect my contract?
- How will changes in interest rates affect my contract?

# Overview
Select:
- Call or put,
- Input ticker name,
- Input strike,
- Expiration date

# Setup
- Clone repository.
- Use pip install -r requirements.txt to install required modules.
- Run it from terminal with: python main.py
- Follow the link in terminal to local server (open it in browser).

# Sources of financial data
- yfinance module for underlying stock price and option chain
- py_vollib for Black-Sholes calculations

# Assumptions
- The real risk-free rate is 2%

# To-do's
- Put layout and functions in separate files.

