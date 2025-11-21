# app.py - Fyers API Simple Template
"""
Fyers API Integration - Simple REST Approach
No complex dependencies, just requests library
"""

import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(page_title="Fyers API - Live NSE Data", layout="wide")

st.title("🚀 Fyers API - Real Indian Market Data")

# Sidebar for credentials
st.sidebar.header("Fyers Credentials")
st.sidebar.markdown("Get these from: https://myapi.fyers.in/dashboard/")

client_id = st.sidebar.text_input("Client ID (App ID)", help="Your Fyers App ID")
secret_key = st.sidebar.text_input("Secret Key", type="password", help="Your App Secret")
redirect_uri = st.sidebar.text_input("Redirect URI", value="http://127.0.0.1:8000/")

# Main content
st.markdown("""
### 📋 Quick Setup Guide

**Step 1:** Enter your Fyers credentials in the sidebar  
**Step 2:** Copy the login URL below and open in browser  
**Step 3:** Authorize and copy the `auth_code` from redirected URL  
**Step 4:** Paste auth_code below and click Authenticate
""")

# Generate login URL
if client_id and redirect_uri:
    login_url = f"https://api.fyers.in/api/v2/generate-authcode?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state=sample"
    
    st.markdown("### 🔗 Step 2: Login URL")
    st.code(login_url, language='text')
    st.info("⬆️ Click to copy, then paste in browser. After login, you'll be redirected to a URL with auth_code")

# Auth code input
auth_code = st.text_input("Step 3: Paste your auth_code here:", type="password", 
                          help="Copy from URL like: ...?auth_code=XXXXX&state=sample")

# Authenticate button
if st.button("🔐 Authenticate with Fyers", type="primary"):
    if not all([client_id, secret_key, redirect_uri, auth_code]):
        st.error("⚠️ Please fill all fields: Client ID, Secret Key, and auth_code")
    else:
        with st.spinner("Authenticating..."):
            try:
                # Exchange auth_code for access_token
                token_url = "https://api.fyers.in/api/v2/token"
                payload = {
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "secret_key": secret_key,
                    "redirect_uri": redirect_uri,
                    "code": auth_code
                }
                headers = {"content-type": "application/json"}
                
                response = requests.post(token_url, data=json.dumps(payload), headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "access_token" in data:
                        access_token = data["access_token"]
                        
                        # Store in session
                        st.session_state.access_token = access_token
                        st.session_state.client_id = client_id
                        st.session_state.authenticated = True
                        
                        st.success("✅ Authentication successful!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Authentication failed: {data}")
                else:
                    st.error(f"❌ HTTP Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Show data fetching interface if authenticated
if st.session_state.get('authenticated'):
    st.markdown("---")
    st.success("🟢 Connected to Fyers API")
    
    access_token = st.session_state.access_token
    client_id = st.session_state.client_id
    auth_header = {"Authorization": f"{client_id}:{access_token}"}
    
    # Tabs for different data
    tab1, tab2, tab3 = st.tabs(["📊 Live Quotes", "👤 Profile", "📈 Historical Data"])
    
    with tab1:
        st.subheader("Get Live Market Quotes")
        
        symbol = st.text_input("Enter Symbol", value="NSE:NIFTY50-INDEX", 
                               help="Format: NSE:SYMBOL or NSE:SYMBOL-INDEX")
        
        if st.button("Get Quote", key="quote_btn"):
            try:
                quote_url = "https://api.fyers.in/data-rest/v2/quotes/"
                params = {"symbols": symbol}
                response = requests.get(quote_url, params=params, headers=auth_header)
                
                if response.status_code == 200:
                    data = response.json()
                    st.json(data)
                    
                    # Pretty display
                    if "d" in data and len(data["d"]) > 0:
                        quote = data["d"][0]["v"]
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Last Price", f"₹{quote.get('lp', 0):,.2f}")
                        col2.metric("Change", f"{quote.get('ch', 0):,.2f}")
                        col3.metric("Change %", f"{quote.get('chp', 0):.2f}%")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Your Profile")
        
        if st.button("Get Profile", key="profile_btn"):
            try:
                profile_url = "https://api.fyers.in/api/v2/profile"
                response = requests.get(profile_url, headers=auth_header)
                
                if response.status_code == 200:
                    profile = response.json()
                    st.json(profile)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("Historical Data")
        st.info("💡 Note: Historical data requires subscription. Free accounts may have limited access.")
        
        col1, col2 = st.columns(2)
        with col1:
            hist_symbol = st.text_input("Symbol", value="NSE:SBIN-EQ", key="hist_symbol")
            resolution = st.selectbox("Resolution", ["1", "5", "15", "60", "D"], index=2)
        
        with col2:
            from_date = st.date_input("From Date")
            to_date = st.date_input("To Date")
        
        if st.button("Get Historical Data", key="hist_btn"):
            try:
                hist_url = "https://api.fyers.in/data-rest/v2/history/"
                params = {
                    "symbol": hist_symbol,
                    "resolution": resolution,
                    "date_format": "1",
                    "range_from": str(from_date),
                    "range_to": str(to_date)
                }
                response = requests.get(hist_url, params=params, headers=auth_header)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "candles" in data:
                        # Create DataFrame
                        df = pd.DataFrame(data["candles"], 
                                        columns=["timestamp", "open", "high", "low", "close", "volume"])
                        df["datetime"] = pd.to_datetime(df["timestamp"], unit='s')
                        
                        st.dataframe(df[["datetime", "open", "high", "low", "close", "volume"]], 
                                   use_container_width=True)
                        
                        st.line_chart(df.set_index("datetime")["close"])
                    else:
                        st.warning(f"No data available. Response: {data}")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#666;font-size:12px;'>
<p><strong>Fyers API - Simple REST Integration</strong></p>
<p>No complex dependencies • Uses only requests library • Easy to deploy</p>
<p>⚠️ Keep your credentials secure • Never share access tokens publicly</p>
</div>
""", unsafe_allow_html=True)
