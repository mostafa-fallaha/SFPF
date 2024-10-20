import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import yfinance as yf
import datetime

pd.set_option('display.max_columns', None)

st.set_page_config(
    page_title="Stocks and Forex Forecasts"
)

st.markdown('''
    ## Stocks and Forex Forecasts
    ##### This app will forecast the price to a specific date
''')

options_list = ['AAPL', 'GC=F']
forecast_options = ["Week", "Month"]

forecast_options_dict = {
    "Week": 7,
    "Month": 30,
}

st.sidebar.title("Data")

option = st.sidebar.selectbox("What do you want to forecast", options_list)
date_option = st.sidebar.selectbox("Predict the next?", forecast_options)
submit = st.sidebar.button("Predict")

if submit:
    data = yf.download(option, start="2020-01-01", end=str(datetime.date.today()))

    df = data[['Close']].copy()
    df.rename(columns={'Close': 'Price'}, inplace=True)

    df_daily = df.resample('D').mean().round(1)
    df_daily = df_daily.ffill()

    window_size = 7

    end_date = str(datetime.date.today() + datetime.timedelta(days=forecast_options_dict[date_option]))
    dates = pd.date_range(start=str(datetime.date.today()), end=end_date, freq='D')

    forecast_days = [pd.Timestamp(date, tz='UTC') for date in dates]

    df_rolling = df_daily.rolling(window_size).mean().round(1)
    df_rolling.rename(columns={'Price': 'Rolling_Avg'}, inplace=True)

    forecasts = []
    for i, day in enumerate(forecast_days):
        last_rolling_avg = df_rolling['Rolling_Avg'].iloc[-1]
        forecasts.append(last_rolling_avg)

        df_rolling.loc[day] = last_rolling_avg
        df_rolling['Rolling_Avg'] = df_rolling['Rolling_Avg'].rolling(window_size).mean().round(1)

    ts_forecasts = pd.DataFrame(forecasts, index=pd.to_datetime(forecast_days))

    fig = px.line(df_daily, y='Price', title="Chart")
    fig.update_traces(hovertemplate='Date=%{x}<br>Value=%{y}', line_color="#0077b6")
    fig.add_scatter(x=ts_forecasts.index, y=forecasts, mode='lines', name='Predicted', line=dict(dash='dash', color='red'))

    fig.update_layout(
            title_x=0.5,
            legend=dict(orientation='v', x=0.1, xanchor='center'),
            plot_bgcolor='#111',  # Plot area background
            # paper_bgcolor='rgba(255, 255, 255, 0.9)',  # Overall background
        )
    st.plotly_chart(fig)

    st.write('for the day:', ts_forecasts.iloc[-1].name.date())
    st.write("values is:", ts_forecasts.iloc[-1, 0])