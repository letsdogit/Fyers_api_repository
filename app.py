import streamlit as st
from fyers_apiv2 import fyersModel
from fyers_apiv2 import accessToken
import requests
import json

st.title("Fyers API – India Live Data Demo")

# Sidebar for API setup
st.sidebar.header("Enter Fyers API Credentials")
client_id = st.sidebar.text_input("Client ID (App ID)")
secret_key = st.sidebar.text_input("Secret Key", type="password")
redirect_uri = st.sidebar.text_input("Redirect URI", value="http://127.0.0.1:8000/", help="Use whatever you set in app dashboard.")

# Instructions
st.markdown("""
#### Step-by-step to authenticate:
1. Enter your API credentials and redirect URL in the sidebar.
2. Copy this URL and open in browser:
""")

if client_id and redirect_uri:
    login_url = f"https://api.fyers.in/api/v2/generate-authcode?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state=sample"
    st.code(login_url, language='none')
    st.write("**Copy `auth_code` from URL after logging in and being redirected.**")

# Input for auth code
auth_code = st.text_input("Paste the `auth_code` here (from redirected URL):", key="auth_code")

# Generate access token
if st.button("Authenticate with Fyers") and all([client_id, secret_key, redirect_uri, auth_code]):
    session = accessToken.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type="code",
        grant_type="authorization_code"
    )
    session.auth_code = auth_code
    response = session.generate_token()
    if "access_token" in response:
        access_token = response["access_token"]
        st.success("Fyers API authentication successful!")
        st.balloons()

        # Connect to Fyers API
        fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path=".")

        # Example: Get NIFTY Spot
        st.header("NSE India Live Data Examples")
        nifty_spot = fyers.quotes({"symbols":"NSE:NIFTY50-INDEX"})
        st.write("NIFTY 50 Spot:", nifty_spot["d"][0]["v"]["lp"])

        # Example: Option chain (showing 10 NIFTY options for today)
        st.subheader("Nifty Option Quotes (first expiry)")
        info = fyers.get_option_chain({"symbol":"NSE:NIFTY50-INDEX"})
        first_expiry = info["1"]["v"]["expiryDates"][0]
        contracts = [x for x in info["2"] if x["expiry"] == first_expiry][:10]
        st.dataframe(pd.DataFrame(contracts)[["symbol", "optionType", "strike", "lastTradedPrice", "bidPrice", "askPrice", "openInterest"]])

        # You can now proceed to implement GANN or options logic using Fyers real data!
    else:
        st.error(f"Authentication failed: {response}")

else:
    st.info("Fill credentials and follow the steps above to authenticate.")

st.markdown("""
---

*For production, never expose your secret keys. Run this only in your own secure environment.*
""")
