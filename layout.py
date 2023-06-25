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

# Generate list of dates for expiration date dropdown
today = date.today()
next_3_months = [
    today + timedelta(days=x) for x in range(90)
]
date_strings = [
    d.strftime("%Y-%m-%d") for d in next_3_months
]

layout = html.Div(
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
