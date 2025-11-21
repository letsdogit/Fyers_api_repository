import streamlit as st
from kiteconnect import KiteConnect

st.title("NSE Live Data - Zerodha Kite")
api_key = st.secrets["API_KEY"]
api_secret = st.secrets["API_SECRET"]

kite = KiteConnect(api_key=api_key)
st.markdown(f"[Login to your Zerodha account here to get your request_token.]({kite.login_url()})")

request_token = st.text_input("Paste your request_token from the redirect URL here:")

if request_token:
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        kite.set_access_token(access_token)
        st.success("Authenticated with Zerodha Kite API!")
        # Example live data call
        price = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
        st.write(f"NIFTY Spot Price: ₹{price}")
        # ... extend with your analytics, GANN logic, backtester, etc ...
    except Exception as e:
        st.error(f"Login failed: {e}")
