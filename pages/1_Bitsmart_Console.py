import streamlit as st
import plotly.graph_objects as go
from keras.models import load_model
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from datetime import timedelta, datetime

st.set_page_config(page_title="BitSmart Prediction Console", layout="wide")

todayDate = datetime.today().date()

# Title section
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.write("")
with col2:
    st.title("BitSmart Prediction Console")
with col3:
    st.write("")


# Input section with date picker

today = st.date_input("Assume today's date is:", max_value=todayDate)


# Load the trained model
today += timedelta(days=1)
model = load_model("model.h5")
stocks = ['BTC-USD']
stock = stocks[0]
stock_data = yf.download(stock, start='2022-01-01', end=today.strftime("%Y-%m-%d"))
ohlc = stock_data[['Open', 'High', 'Low', 'Close']].values
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_ohlc = scaler.fit_transform(ohlc)
predicted_prices = []
seq_length = 60
last_seq = ohlc[-seq_length:]
predictions = {}

for _ in range(7):
    last_seq_scaled = scaler.transform(last_seq)
    next_day_scaled = model.predict(np.array([last_seq_scaled]))
    next_day = scaler.inverse_transform(next_day_scaled)[0]
    predicted_prices.append(next_day)
    last_seq = np.append(last_seq[1:], [next_day], axis=0)


# Convert predicted prices to DataFrame with dates
date_range = pd.date_range(start=stock_data.index[-1] + timedelta(days=1), periods=7)
predicted_df = pd.DataFrame(predicted_prices, columns=['Open', 'High', 'Low', 'Close'], index=date_range)
predicted_df.index = predicted_df.index.strftime('%Y-%m-%d') 


# Add the predicted prices to the dictionary
predictions[stock] = predicted_df

# Print the predictions
print(predictions)

prices = predicted_df['Close'].tolist()
high_prices = predicted_df['High'].tolist()
low_prices = predicted_df['Low'].tolist()


# Display table with predicted values and Predicted Prices (USD) section
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Predicted Prices (USD)")
    st.write("Highest Price:", max(high_prices))
    st.write("Lowest Price:", min(low_prices))
    st.write("Average Closing Price:", sum(prices) / len(prices))

with col2:
    st.subheader("Predicted Prices Table")
    st.dataframe(predicted_df)

def create_chart(chart_type, fig_height, fig_width):
    fig = None
    if chart_type == "Candlestick":
        fig = go.Figure(
        data=[go.Candlestick(
            x=predicted_df.index,
            open=predicted_df['Open'],
            high=predicted_df['High'],
            low=predicted_df['Low'],
            close=predicted_df['Close']
            )],
            layout={
                "title": "Predicted Prices for the Next Seven Days (USD)",
                "xaxis_title": "Date",
                "yaxis_title": "Price (USD)",
                "height": fig_height,  
                "width": fig_width,
            }
        )
        
    elif chart_type == "OHLC":
        fig = go.Figure(
            data=[go.Ohlc(
                x=predicted_df.index,
                open=predicted_df['Open'],
                high=predicted_df['High'],
                low=predicted_df['Low'],
                close=predicted_df['Close']
            )],
            layout={
                "title": "Predicted Prices for the Next Seven Days (USD)",
                "xaxis_title": "Date",
                "yaxis_title": "Price (USD)",
                "height": fig_height,  
                "width": fig_width,
            }
        )
    elif chart_type == "Combination":
        fig = go.Figure()

        # Add Candlestick chart
        fig.add_trace(go.Candlestick(
            x=predicted_df.index,
            open=predicted_df['Open'],
            high=predicted_df['High'],
            low=predicted_df['Low'],
            close=predicted_df['Close'],
            name='Candlestick'
        ))

        # Add Line chart
        fig.add_trace(go.Scatter(
            x=predicted_df.index,
            y=predicted_df['Close'],
            mode='lines+markers',
            name='Close Price'
        ))

        fig.update_layout(
            title="Predicted Prices for the Next Seven Days (USD)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=fig_height,
            width=fig_width
        )

    return fig


def data_chart(Data_type, fig_height, fig_width):
    fig = None
    if Data_type == "Close":
            fig = go.Figure(
                data=[go.Scatter(
                    x=predicted_df.index,
                    y=predicted_df['Close'],
                    mode='lines+markers',
                    name='Close',
                    line=dict(color='red')
                )],
                layout={
                    "title": f"Predicted Prices for the Next Seven Days (USD) - {Data_type}",
                    "xaxis_title": "Date",
                    "yaxis_title": f"Price ({Data_type})",
                    "height": fig_height,  
                    "width": fig_width,
                }
            )
    elif Data_type == "High":
            fig = go.Figure(
                data=[go.Scatter(
                    x=predicted_df.index,
                    y=predicted_df['High'],
                    mode='lines+markers',
                    name='High',
                    line=dict(color='red')
                )],
                layout={
                    "title": f"Predicted Prices for the Next Seven Days (USD) - {Data_type}",
                    "xaxis_title": "Date",
                    "yaxis_title": f"Price ({Data_type})",
                    "height": fig_height,  
                    "width": fig_width,
                }
            )
    elif Data_type == "Open":
            fig = go.Figure(
                data=[go.Scatter(
                    x=predicted_df.index,
                    y=predicted_df['Open'],
                    mode='lines+markers',
                    name='Open',
                    line=dict(color='red')
                )],
                layout={
                    "title": f"Predicted Prices for the Next Seven Days (USD) - {Data_type}",
                    "xaxis_title": "Date",
                    "yaxis_title": f"Price ({Data_type})",
                    "height": fig_height,  
                    "width": fig_width,
                }
            ) 
    elif Data_type == "Low":
            fig = go.Figure(
                data=[go.Scatter(
                    x=predicted_df.index,
                    y=predicted_df['Low'],
                    mode='lines+markers',
                    name='Low'
                )],
                layout={
                    "title": f"Predicted Prices for the Next Seven Days (USD) - {Data_type}",
                    "xaxis_title": "Date",
                    "yaxis_title": f"Price ({Data_type})",
                    "height": fig_height,  
                    "width": fig_width,
                }
            )
    return fig


# Display the charts side by side
col1, col2 = st.columns(2)
with col1:
    # Chart type selection
    chart_type = st.selectbox("Select Chart Type",("Candlestick", "OHLC", "Combination"))
    st.plotly_chart(create_chart(chart_type, fig_width=550, fig_height=450))
with col2:
    # Chart type selection
    Data_type = st.selectbox("Select Data Type for Single plot", ("Close", "High", "Open", "Low"))
    st.plotly_chart(data_chart(Data_type, fig_width=550, fig_height=450))

def swing_trade_fn(df):
    # Convert index to datetime if it is not already
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)
    
    # Initial investment
    initial_investment = 100000
    initial_price = df.iloc[0]['Open']
    btc_amount = initial_investment / initial_price
    
    # Create a list to hold trade details
    trades = []
    trades.append({
        'Command': 'Initial Buy',
        'Date': df.index[0].date(),
        'Price': initial_price,
        'Amount': btc_amount,
        'R/I': initial_investment
    })
    
    # Initialize variables for trading
    initial_buy_date = df.index[0]
    buy_date = initial_buy_date
    sell_date = None
    holding_btc = True
    max_profit = -float('inf')
    transaction_done = False

    # Find the best sell day after initial buy
    for i in range(1, len(df)):
        if holding_btc:
            current_sell_price = df.iloc[i]['High']
            potential_profit = (current_sell_price - initial_price) * btc_amount

            if potential_profit > max_profit:
                max_profit = potential_profit
                sell_date = df.index[i]
                sell_price = current_sell_price

    # Perform the initial sell at the identified optimal day
    if holding_btc:
        trades.append({
            'Command': 'First Sell',
            'Date': sell_date.date(),
            'Price': sell_price,
            'Amount': btc_amount,
            'R/I': btc_amount * sell_price
        })
        holding_btc = False
        transaction_done = True

    # After selling, look for the best re-buy opportunity
    if transaction_done:
        max_profit = -float('inf')
        for i in range(df.index.get_loc(sell_date) + 1, len(df)):
            current_buy_price = df.iloc[i]['Low']
            potential_profit = (df.iloc[-1]['Close'] - current_buy_price) * btc_amount

            if potential_profit > max_profit:
                max_profit = potential_profit
                buy_date = df.index[i]
                buy_price = current_buy_price

        # Perform the re-buy and final sell
        if max_profit > 0:
            btc_amount = (btc_amount * sell_price) / buy_price
            trades.append({
                'Command': 'Re-Buy',
                'Date': buy_date.date(),
                'Price': buy_price,
                'Amount': btc_amount,
                'R/I': btc_amount * buy_price
            })

            final_sell_price = df.iloc[-1]['Close']
            trades.append({
                'Command': 'Final Sell',
                'Date': df.index[-1].date(),
                'Price': final_sell_price,
                'Amount': btc_amount,
                'R/I': btc_amount * final_sell_price
            })

    # Final check to ensure no holding BTC at the end of the week
    if holding_btc:
        final_close_price = df.iloc[-1]['Close']
        trades.append({
            'Command': 'Final Sell',
            'Date': df.index[-1].date(),
            'Price': final_close_price,
            'Amount': btc_amount,
            'R/I': btc_amount * final_close_price
        })
    
    return pd.DataFrame(trades)

# Trading strategy section
trade_df = swing_trade_fn(predicted_df)

col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.write("")
with col2:
    st.subheader("Recommended Swing Trading Strategy:")
with col3:
    st.write("")

# Add the table to the Streamlit app
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Command and Date")
    for index, row in trade_df.iterrows():
        st.write(f"{row['Command']}: {row['Date']}")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

with col2:
    st.subheader("Price, Amount and R/I")
    for index, row in trade_df.iterrows():
        st.write(f"Price: {row['Price']:.2f}")
        st.write(f"Amount: {row['Amount']:.6f} BTC")
        st.write(f"R/I: ${row['R/I']:.2f}")
        st.write("")

# Disclaimer section

st.write("---")
st.write(
    'Note: This is a sample prediction and may not be accurate. Please do your own research '
    'before making any investment decisions.')
