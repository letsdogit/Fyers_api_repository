# app.py - Fyers API v3 FIXED - Working Quotes & Historical Data
"""
Fyers API v3 Integration - CORRECTED endpoints for quotes and history
"""

import streamlit as st
import requests
import json
import pandas as pd
import hashlib

st.set_page_config(page_title="Fyers API v3 - Live NSE Data", layout="wide")

st.title("🚀 Fyers API v3 - Real Indian Market Data")

# Sidebar for credentials
st.sidebar.header("Fyers API v3 Credentials")
st.sidebar.markdown("Get these from: https://myapi.fyers.in/dashboard/")

app_id = st.sidebar.text_input("App ID", help="Your Fyers App ID (format: XXXXX-100)")
secret_key = st.sidebar.text_input("Secret Key", type="password", help="Your App Secret")
redirect_uri = st.sidebar.text_input("Redirect URI", value="https://127.0.0.1/")

# Main content
st.markdown("""
### 📋 Fyers API v3 Setup Guide

**Step 1:** Enter your App ID and Secret Key in the sidebar  
**Step 2:** Click "Generate Login URL" below  
**Step 3:** Open the URL in browser and authorize  
**Step 4:** Copy the `auth_code` from redirected URL  
**Step 5:** Paste auth_code and click Authenticate
""")

# Generate app_id_hash (required for v3)
app_id_hash = ""
if app_id and secret_key:
    hash_string = f"{app_id}:{secret_key}"
    app_id_hash = hashlib.sha256(hash_string.encode()).hexdigest()
    st.info(f"✅ App ID Hash generated: {app_id_hash[:20]}...")

# Generate login URL
if app_id and redirect_uri:
    login_url = f"https://api-t1.fyers.in/api/v3/generate-authcode?client_id={app_id}&redirect_uri={redirect_uri}&response_type=code&state=sample_state"
    
    if st.button("📋 Generate Login URL", key="gen_url"):
        st.markdown("### 🔗 Step 2: Copy this URL and open in browser")
        st.code(login_url, language='text')
        st.info("⬆️ After login, you'll be redirected. Copy the `auth_code` from the URL")

# Auth code input
st.markdown("---")
auth_code_raw = st.text_input("Step 4: Paste your auth_code here:", type="password")

# Clean auth_code
auth_code = ""
if auth_code_raw:
    if "&state=" in auth_code_raw:
        auth_code = auth_code_raw.split("&state=")[0]
    elif "auth_code=" in auth_code_raw:
        auth_code = auth_code_raw.split("auth_code=")[1].split("&")[0]
    else:
        auth_code = auth_code_raw.strip()

# Authenticate button
if st.button("🔐 Authenticate with Fyers v3", type="primary"):
    if not all([app_id, secret_key, auth_code]):
        st.error("⚠️ Please fill all fields")
    else:
        with st.spinner("Authenticating..."):
            try:
                token_url = "https://api-t1.fyers.in/api/v3/validate-authcode"
                payload = {
                    "grant_type": "authorization_code",
                    "appIdHash": app_id_hash,
                    "code": auth_code
                }
                headers = {"Content-Type": "application/json"}
                response = requests.post(token_url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("s") == "ok" and "access_token" in data:
                        st.session_state.access_token = data["access_token"]
                        st.session_state.app_id = app_id
                        st.session_state.authenticated = True
                        st.success("✅ Authentication successful!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {data}")
                else:
                    st.error(f"❌ HTTP Error {response.status_code}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Show data interface if authenticated
if st.session_state.get('authenticated'):
    st.markdown("---")
    st.success("🟢 Connected to Fyers API v3")
    
    access_token = st.session_state.access_token
    app_id = st.session_state.app_id
    auth_header = {"Authorization": f"{app_id}:{access_token}"}
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Live Quotes", "👤 Profile", "📈 Historical Data"])
    
    with tab1:
        st.subheader("Live Market Quotes")
        symbol = st.text_input("Enter Symbol", value="NSE:NIFTYBANK-INDEX")
        
        if st.button("Get Quote", key="quote_btn"):
            try:
                # FIXED: Query parameter directly in URL
                quote_url = f"https://api-t1.fyers.in/data-rest/v3/quotes/?symbols={symbol}"
                response = requests.get(quote_url, headers=auth_header)
                
                st.write(f"🔍 Request: {quote_url}")
                st.write(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    st.json(data)
                    
                    if "d" in data and len(data["d"]) > 0:
                        quote = data["d"][0]["v"]
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Last Price", f"₹{quote.get('lp', 0):,.2f}")
                        col2.metric("Volume", f"{quote.get('volume', 0):,.0f}")
                        col3.metric("Change %", f"{quote.get('ch_per', 0):.2f}%")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Your Profile")
        if st.button("Get Profile", key="profile_btn"):
            try:
                profile_url = "https://api-t1.fyers.in/api/v3/profile"
                response = requests.get(profile_url, headers=auth_header)
                
                if response.status_code == 200:
                    profile = response.json()
                    st.json(profile)
                    if "data" in profile:
                        st.success(f"✅ Name: {profile['data'].get('name', 'N/A')}")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("Historical Data")
        st.info("💡 Requires historical data subscription")
        
        col1, col2 = st.columns(2)
        with col1:
            hist_symbol = st.text_input("Symbol", value="NSE:SBIN-EQ", key="hist_symbol")
            resolution = st.selectbox("Resolution", ["1", "5", "15", "60", "D"], index=2)
        with col2:
            from_date = st.date_input("From Date")
            to_date = st.date_input("To Date")
        
        if st.button("Get Historical Data", key="hist_btn"):
            try:
                # FIXED: Date format and URL construction
                from_str = from_date.strftime("%Y-%m-%d")
                to_str = to_date.strftime("%Y-%m-%d")
                
                hist_url = f"https://api-t1.fyers.in/data-rest/v3/history/?symbol={hist_symbol}&resolution={resolution}&date_format=1&range_from={from_str}&range_to={to_str}&cont_flag=1"
                
                response = requests.get(hist_url, headers=auth_header)
                
                st.write(f"🔍 Request: {hist_url}")
                st.write(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    st.json(data)
                    
                    if "candles" in data:
                        df = pd.DataFrame(data["candles"], 
                                        columns=["date", "open", "high", "low", "close", "volume"])
                        st.dataframe(df, use_container_width=True, height=300)
                        st.line_chart(df.set_index("date")["close"])
                    else:
                        st.warning(f"No data: {data}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

# Logout
if st.session_state.get('authenticated'):
    st.markdown("---")
    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.rerun()

st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#666;font-size:12px;'>
<p><strong>Fyers API v3 - FIXED Version</strong></p>
<p>✅ Corrected endpoints for quotes and historical data</p>
</div>
""", unsafe_allow_html=True)
