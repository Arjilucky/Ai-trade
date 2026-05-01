import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

# --- App Configuration ---
st.set_page_config(page_title="Market Analyzer Pro", layout="wide")
st.title("📈 AI Market Analyzer & Signal Generator")

# --- Sidebar Inputs ---
st.sidebar.header("Analysis Parameters")
# Defaulting to Apple, but compatible with any Yahoo/TradingView ticker (e.g., RELIANCE.NS, BTC-USD)
symbol = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL").upper()
days_to_analyze = st.sidebar.slider("Historical Data Days", 30, 365, 180)

# --- Section 1: TradingView Integration ---
st.subheader(f"TradingView Advanced Chart: {symbol}")

# TradingView HTML/JS Widget Code
# We dynamically inject the user's chosen symbol into the widget
tv_widget = f"""
<div class="tradingview-widget-container">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {{
  "width": "100%",
  "height": 500,
  "symbol": "{symbol}",
  "interval": "D",
  "timezone": "Etc/UTC",
  "theme": "dark",
  "style": "1",
  "locale": "en",
  "enable_publishing": false,
  "allow_symbol_change": true,
  "container_id": "tradingview_chart"
}}
  );
  </script>
</div>
"""
# Render the widget in Streamlit
components.html(tv_widget, height=500)
# --- Section 2: Python Data Analysis & Signals ---
st.subheader("Python Analysis Engine")

@st.cache_data
def load_data(ticker, days):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    return df

try:
    # Fetch Data
    data = load_data(symbol, days_to_analyze)
    
    if data.empty:
        st.error(f"No data found for {symbol}. Please check the ticker symbol.")
    else:
        # Calculate Technical Indicators
        data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
        data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
        data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
        
        # Get latest data points
        latest_close = data['Close'].iloc[-1]
        latest_rsi = data['RSI'].iloc[-1]
        sma_20 = data['SMA_20'].iloc[-1]
        sma_50 = data['SMA_50'].iloc[-1]
        
        # --- Basic Signal Logic Engine ---
        # This is where your AI/ML logic would eventually go.
        # For now, we use a basic momentum and moving average crossover strategy.
        signal = "HOLD 🟡"
        reason = "Market is consolidating or indicators are neutral."
        
        if sma_20 > sma_50 and latest_rsi < 70:
            signal = "BUY 🟢"
            reason = "Short-term momentum (SMA 20) is above long-term (SMA 50) and asset is not overbought (RSI < 70)."
        elif sma_20 < sma_50 or latest_rsi >= 70:
            signal = "SELL 🔴"
            reason = "Short-term momentum is lagging, or the asset is heavily overbought (RSI > 70)."
            
        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Latest Close", f"${latest_close:.2f}")
        col2.metric("RSI (14)", f"{latest_rsi:.2f}")
        col3.metric("SMA 20", f"${sma_20:.2f}")
        col4.metric("SMA 50", f"${sma_50:.2f}")
        
        # Display Signal
        st.markdown(f"### Current System Signal: **{signal}**")
        st.info(f"**Reasoning:** {reason}")
        
        # Show raw data toggle
        with st.expander("View Raw Technical Data"):
            st.dataframe(data.tail(10))

except Exception as e:
    st.error(f"An error occurred fetching data: {e}")

# --- Disclaimer ---
st.markdown("---")
st.caption("⚠️ **Disclaimer:** This application is for educational purposes only. The Buy/Sell signals are generated using basic moving averages and RSI, which do not constitute professional financial advice. Always do your own research before trading.")
