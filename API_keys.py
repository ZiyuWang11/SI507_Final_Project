import requests
import plotly.graph_objects as go
import pandas as pd
import datetime


KEY = "bva40sn48v6t3lvcodk0"
df = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=AAPL&resolution=D&from=1591937072&to=1607748272&token=bva40sn48v6t3lvcodk0')
df = df.json()
time = []
for i in range(len(df['t'])):
    time.append(datetime.datetime.fromtimestamp(df['t'][i]))

fig = go.Figure(data=[go.Candlestick(x=time,
                open=df['o'], high=df['h'],
                low=df['l'], close=df['c'])
                     ])

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()