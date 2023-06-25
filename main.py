import pandas
import dash
from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
    State,
    dash_table,
)
from loguru import logger
import webbrowser
import yfinance as yf
import py_vollib.black_scholes as bs
import py_vollib.black_scholes.greeks.analytical as bs_greeks
from datetime import date, timedelta, datetime

pandas.set_option("display.max_columns", None)
pandas.set_option("display.max_rows", None)
pandas.options.display.float_format = "{:,.2f}".format
pandas.set_option("display.max_columns", None)

# Generate list of dates for expiration date dropdown
today = date.today()
next_3_months = [
    today + timedelta(days=x) for x in range(90)
]
date_strings = [
    d.strftime("%Y-%m-%d") for d in next_3_months
]


app = Dash(__name__)

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "Options Helper App",
                    style={
                        "text-align": "left",
                        "font-size": "32px",
                    },
                ),
                html.P("Please Select Call or Put:"),
                dcc.Dropdown(
                    ["call", "put"],
                    id="calls-or-puts-dropdown",
                    style={"width": "150px"},
                ),
                html.Br(),
                dcc.Store(
                    id="calls-or-puts-dropdown-value"
                ),
                html.P("Please Input the Ticker:"),
                dcc.Input(
                    id="ticker",
                    placeholder="Input Stock Ticker",
                    style={
                        "height": "33px",
                        "width": "150px",
                        "font-size": "14px",
                    },
                ),
                html.Br(),
                dcc.Store(id="ticker-output"),
                html.Br(),
                html.P("Please Input the Strike:"),
                dcc.Input(
                    id="strike-input",
                    placeholder="Input Strike",
                    style={
                        "height": "33px",
                        "width": "150px",
                        "font-size": "14px",
                    },
                ),
                html.Br(),
                dcc.Store(id="selected-option-chain-row"),
                dcc.Store(
                    id="ready-for-Black-Scholes-dict"
                ),
                dcc.Store(
                    id="selected-expiration-date-dropdown-value"
                ),
                dcc.Store(id="strike-output-value"),
                dcc.Store(id="the-greeks"),
                html.Br(),
                html.P(
                    "Please Select the Expiration Date:"
                ),
                dcc.Dropdown(
                    id="select-expiration-date-dropdown",
                    options=[
                        {"label": d, "value": d}
                        for d in date_strings
                    ],
                    value=date_strings[0],
                    style={"width": "150px"},
                ),
                html.Br(),
                html.Button(
                    "Get the Greeks!",
                    id="submit-button",
                    n_clicks=0,
                    style={
                        "color": "white",
                        "background-color": "#0074D9",
                        "border-radius": "50px",
                        "padding": "10px 20px",
                        "margin-bottom": "20px",
                        "font-size": "14px",
                    },
                ),
            ],
            style={
                "display": "inline-block",
                "vertical-align": "top",
                "width": "45%",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Contract Overview",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                        html.Div(
                            id="contract-overview",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                    ],
                    style={
                        "border": "2px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "margin": "20px",
                        "background-color": "#f9f9f9",
                        "box-shadow": "2px 2px 2px lightgrey",
                        "width": "300px",
                        "align-items": "center",
                    },
                ),
                html.Div(
                    [
                        html.P(
                            "Delta",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                        html.Div(
                            id="delta-output",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                    ],
                    style={
                        "border": "2px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "margin": "20px",
                        "background-color": "#f9f9f9",
                        "box-shadow": "2px 2px 2px lightgrey",
                        "width": "300px",
                        "align-items": "center",
                    },
                ),
                html.Div(
                    [
                        html.P(
                            "Gamma",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                        html.Div(
                            id="gamma-output",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                    ],
                    style={
                        "border": "2px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "margin": "20px",
                        "background-color": "#f9f9f9",
                        "box-shadow": "2px 2px 2px lightgrey",
                        "width": "300px",
                    },
                ),
                html.Div(
                    [
                        html.P(
                            "Theta",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                        html.Div(
                            id="theta-output",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                    ],
                    style={
                        "border": "2px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "margin": "20px",
                        "background-color": "#f9f9f9",
                        "box-shadow": "2px 2px 2px lightgrey",
                        "width": "300px",
                    },
                ),
                html.Div(
                    [
                        html.P(
                            "Vega",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                        html.Div(
                            id="vega-output",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                    ],
                    style={
                        "border": "2px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "margin": "20px",
                        "background-color": "#f9f9f9",
                        "box-shadow": "2px 2px 2px lightgrey",
                        "width": "300px",
                    },
                ),
                html.Div(
                    [
                        html.P(
                            "Rho",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                        html.Div(
                            id="rho-output",
                            style={
                                "text-align": "center",
                                "fontSize": 24,
                            },
                        ),
                    ],
                    style={
                        "border": "2px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "margin": "20px",
                        "background-color": "#f9f9f9",
                        "box-shadow": "2px 2px 2px lightgrey",
                        "width": "300px",
                    },
                ),
            ]
        ),
    ]
)


# Get call or puts decision
@app.callback(
    Output("calls-or-puts-dropdown-value", "data"),
    Input("calls-or-puts-dropdown", "value"),
    prevent_initial_call=True,
)
def update_call_or_puts_callback(call_or_puts_decision):
    if call_or_puts_decision is not None:
        call_or_puts_decision = (
            call_or_puts_decision.lower()
        )
        return call_or_puts_decision


@app.callback(
    Output("ticker-output", "data"),
    Output("strike-output-value", "data"),
    Input("ticker", "value"),
    Input("calls-or-puts-dropdown", "value"),
    Input("submit-button", "n_clicks"),
    Input("strike-input", "value"),
    prevent_initial_call=True,
)
def get_the_tickers_and_strike_data(
    ticker_value,
    n_clicks_calls_puts_dropdown,
    n_clicks_submit_ticker,
    strike_input,
):
    if (
        ticker_value is not None
        and n_clicks_calls_puts_dropdown is not None
        and n_clicks_submit_ticker > 0
        and strike_input is not None
    ):
        ticker_value = ticker_value.upper()
    return ticker_value, strike_input


# Get desired expiration date
@app.callback(
    Output(
        "selected-expiration-date-dropdown-value", "data"
    ),
    Input("select-expiration-date-dropdown", "value"),
    prevent_initial_call=True,
)
def update_call_or_puts_callback(date):
    logger.debug(date)
    return date


@app.callback(
    Output("selected-option-chain-row", "data"),
    Input("calls-or-puts-dropdown", "value"),
    Input("ticker-output", "data"),
    Input(
        "selected-expiration-date-dropdown-value", "data"
    ),
    Input("strike-output-value", "data"),
    Input("submit-button", "n_clicks"),
    prevent_initial_call=True,
)
def get_the_initial_option_chain_data(
    call_or_put_choice,
    ticker_value,
    desired_expiration_date,
    desired_strike,
    submit_button,
):
    if (
        call_or_put_choice is not None
        and ticker_value is not None
        and desired_expiration_date is not None
        and desired_strike is not None
        and submit_button is not None
    ):
        # Get the current ask of the stock
        ticker_dict = yf.Ticker(ticker_value).info
        if ticker_dict["ask"] == 0:
            stock_current_price = ticker_dict[
                "previousClose"
            ]
        else:
            stock_current_price = ticker_dict["ask"]
        # Get row in option chain
        ticker_obj = yf.Ticker(ticker_value)
        if "call" in call_or_put_choice:
            options_chain = ticker_obj.option_chain(
                desired_expiration_date
            ).calls
            options_chain = options_chain[
                options_chain["strike"]
                == float(desired_strike)
            ]
            options_chain = options_chain.to_dict(
                orient="index"
            )
            options_chain[
                "current_ask"
            ] = stock_current_price
            logger.debug(stock_current_price)
            logger.debug(options_chain)
            return options_chain
        elif "call" in call_or_put_choice and ValueError:
            return "Not a valid strike date"
        elif "put" in call_or_put_choice:
            options_chain = ticker_obj.option_chain(
                desired_expiration_date
            ).puts
            options_chain = options_chain[
                options_chain["strike"]
                == float(desired_strike)
            ]
            options_chain = options_chain.to_dict(
                orient="index"
            )
            options_chain[
                "current_ask"
            ] = stock_current_price
            logger.debug(stock_current_price)
            logger.debug(options_chain)
            return options_chain
        else:
            return "Not a valid strike date"


@app.callback(
    Output("ready-for-Black-Scholes-dict", "data"),
    Input("selected-option-chain-row", "data"),
    Input(
        "selected-expiration-date-dropdown-value", "data"
    ),
    Input("submit-button", "n_clicks"),
    prevent_initial_call=True,
)
def get_ready_for_black_sholes_dict(
    option_chain_dict,
    desired_expiration_date,
    submit_button,
):
    if (
        option_chain_dict is not None
        and submit_button is not None
    ):
        desired_expiration_date = datetime.strptime(
            desired_expiration_date, "%Y-%m-%d"
        ).date()
        time_delta_in_years = (
            (desired_expiration_date - today).days
        ) / 365.25
        dict_for_black_sholes = {}
        dict_for_black_sholes["strike"] = (
            next(iter(option_chain_dict.values()))
        )["strike"]
        dict_for_black_sholes[
            "current_ask"
        ] = option_chain_dict["current_ask"]
        dict_for_black_sholes["impliedVolatility"] = (
            next(iter(option_chain_dict.values()))
        )["impliedVolatility"]
        dict_for_black_sholes[
            "time_delta_in_years"
        ] = time_delta_in_years
        logger.debug(dict_for_black_sholes)
        return dict_for_black_sholes


@app.callback(
    Output("the-greeks", "data"),
    Input("ready-for-Black-Scholes-dict", "data"),
    Input("calls-or-puts-dropdown", "value"),
    Input("submit-button", "n_clicks"),
    prevent_initial_call=True,
)
def calculate_the_greeks(
    ready_for_black_sholes_dict,
    call_or_put_choice,
    submit_button,
):
    if (
        ready_for_black_sholes_dict is not None
        and submit_button is not None
        and call_or_put_choice is not None
    ):
        underlying_price = ready_for_black_sholes_dict[
            "current_ask"
        ]
        strike_price = ready_for_black_sholes_dict["strike"]
        time_to_maturity = round(
            ready_for_black_sholes_dict[
                "time_delta_in_years"
            ],
            2,
        )
        risk_free_interest_rate = 0.02
        implied_volatility = round(
            ready_for_black_sholes_dict[
                "impliedVolatility"
            ],
            2,
        )

        greeks = {}
        if call_or_put_choice.startswith("call"):
            option_type = "c"
        elif call_or_put_choice.startswith("put"):
            option_type = "p"

        option_price = bs.black_scholes(
            option_type,
            underlying_price,
            strike_price,
            time_to_maturity,
            risk_free_interest_rate,
            implied_volatility,
        )
        for greek_name in [
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
        ]:
            greeks[greek_name] = getattr(
                bs_greeks, greek_name
            )(
                option_type,
                underlying_price,
                strike_price,
                time_to_maturity,
                risk_free_interest_rate,
                implied_volatility,
            )
        logger.debug(greeks)
        return greeks

    else:
        return {}


@app.callback(
    Output("delta-output", "children"),
    Input("the-greeks", "data"),
    Input("submit-button", "n_clicks"),
    Input("calls-or-puts-dropdown", "value"),
)
def update_the_delta_output(
    the_greeks_dict, n_clicks_submit, call_or_put_choice
):
    if (
        the_greeks_dict is not None
        and n_clicks_submit > 0
        and call_or_put_choice is not None
    ):
        if (
            "call" in call_or_put_choice
            and call_or_put_choice
        ):
            delta = round(the_greeks_dict["delta"], 8)
            return (
                f"According to Black-Sholes, this contract has a {round(delta * 100,2)}% chance of being profitable. "
                f"Given a $1 change in underlying this call will likely gain or lose"
                f" the same amount of money as {round(delta * 100,2)} shares of stock."
            )
        elif (
            "put" in call_or_put_choice
            and call_or_put_choice
        ):
            delta = round(the_greeks_dict["delta"], 8) * -1
            return (
                f"According to Black-Sholes, this contract has a {round(delta * 100,2)}% chance of being profitable. "
                f"Given a $1 change in underlying this put will likely gain or lose "
                f"the same amount of money as {round(delta * 100,2)} shares of stock."
            )
        else:
            return ""
    else:
        return "Waiting for input..."


@app.callback(
    Output("gamma-output", "children"),
    Input("the-greeks", "data"),
    Input("submit-button", "n_clicks"),
    Input("calls-or-puts-dropdown", "value"),
)
def update_the_gamma_output(
    the_greeks_dict, n_clicks_submit, call_or_put_choice
):
    if (
        call_or_put_choice is not None
        and the_greeks_dict is not None
        and n_clicks_submit > 0
    ):
        gamma = round(the_greeks_dict["gamma"], 8)
        if "call" in call_or_put_choice:
            return (
                f"According to Black-Sholes, this call contract has a gamma of {round(gamma,2)}. "
                f"Given a $1 change in underlying, the delta of this call"
                f" will likely change by {round(gamma * 100,2)}%."
            )
        elif "put" in call_or_put_choice:
            return (
                f"According to Black-Sholes, this put contract has a gamma of {round(gamma,2)}. "
                f"Given a $1 change in underlying, the delta of this put"
                f" will likely change by {round(gamma * 100,2)}%."
            )
        else:
            return ""
    else:
        return "Waiting for input..."


@app.callback(
    Output("theta-output", "children"),
    Input("the-greeks", "data"),
    Input("submit-button", "n_clicks"),
    Input("calls-or-puts-dropdown", "value"),
)
def update_the_theta_output(
    the_greeks_dict, n_clicks_submit, call_or_put_choice
):
    if (
        call_or_put_choice is not None
        and the_greeks_dict is not None
        and n_clicks_submit > 0
    ):
        theta = round(the_greeks_dict["theta"], 8) * -1
        if "call" in call_or_put_choice:
            return (
                f"According to Black-Sholes, this call contract will lose ${round(theta*100,3)} "
                f"every day off of the premium. Note: The effect of theta "
                f"really ramps up 30-45 days from expiration."
            )
        elif "put" in call_or_put_choice:
            return (
                f"According to Black-Sholes, this put contract will lose ${round(theta*100,3)} "
                f"every day off of the premium. Note: The effect of theta"
                f" really ramps up 30-45 days from expiration."
            )
        else:
            return ""
    else:
        return "Waiting for input..."


@app.callback(
    Output("vega-output", "children"),
    Input("the-greeks", "data"),
    Input("submit-button", "n_clicks"),
    Input("calls-or-puts-dropdown", "value"),
)
def update_the_vega_output(
    the_greeks_dict, n_clicks_submit, call_or_put_choice
):
    if (
        call_or_put_choice is not None
        and the_greeks_dict is not None
        and n_clicks_submit > 0
    ):
        vega = round(the_greeks_dict["vega"], 8)
        if "call" in call_or_put_choice:
            return (
                f"With a 1% change in volatility, the value of this call"
                f" contract will change by ${round(vega*100,3)}"
            )
        elif "put" in call_or_put_choice:
            return (
                f"With a 1% change in volatility, the value of this put"
                f" contract will change by ${round(vega*100,3)}"
            )
        else:
            return ""
    else:
        return "Waiting for input..."


@app.callback(
    Output("rho-output", "children"),
    Input("the-greeks", "data"),
    Input("submit-button", "n_clicks"),
    Input("calls-or-puts-dropdown", "value"),
)
def update_the_vega_output(
    the_greeks_dict, n_clicks_submit, call_or_put_choice
):
    if (
        call_or_put_choice is not None
        and the_greeks_dict is not None
        and n_clicks_submit > 0
    ):
        if "call" in call_or_put_choice:
            rho = round(the_greeks_dict["rho"], 8)
            return (
                f"With a 1 percentage point increase in interest rates, the value of this call will decrease by "
                f"{round(rho, 3)*100}%. Note: LEAPS are typically more sensitive to interest rate "
                f"changes than short-term options."
            )
        elif "put" in call_or_put_choice:
            rho = round(the_greeks_dict["rho"], 8) * -1
            return (
                f"With a 1 percentage point increase in interest rates, the value of this put will increase by "
                f"{round(rho, 3)*100}%. Note: LEAPS are typically more sensitive to interest rate "
                f"changes than short-term options."
            )
        else:
            return ""
    else:
        return "Waiting for input..."


@app.callback(
    Output("contract-overview", "children"),
    Input("selected-option-chain-row", "data"),
)
def get_contract_overview(option_chain_row):
    if option_chain_row is not None:
        logger.debug(option_chain_row.keys())
        return (
            f"Current Stock Price: {option_chain_row['current_ask']}\n"
            f"Current Bid: {option_chain_row[next(iter(option_chain_row))]['bid']}\n",
            f"Current Ask: {option_chain_row[next(iter(option_chain_row))]['ask']}\n",
            f"Percent Change: {round(option_chain_row[next(iter(option_chain_row))]['bid'],2)}\n",
            f"Open Interest: {round(option_chain_row[next(iter(option_chain_row))]['openInterest'],2)}\n",
        )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port="8051", debug=False)
