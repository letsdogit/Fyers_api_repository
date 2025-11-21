import streamlit as st
import requests
import json

st.title("Fyers API - Live NSE Data")

st.sidebar.header("Fyers API Credentials")
client_id = st.sidebar.text_input("Client ID (App ID)")
secret_key = st.sidebar.text_input("Secret Key", type="password")
redirect_uri = st.sidebar.text_input("Redirect URI", value="http://127.0.0.1:8000/")

st.markdown("""
### Authentication Steps:
1. Enter your credentials in sidebar
2. Copy the URL below and open in browser
3. Login to Fyers and authorize
4. Copy the `auth_code` from the redirected URL
5. Paste it below
""")

if client_id and redirect_uri:
    login_url = f"https://api.fyers.in/api/v2/generate-authcode?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state=sample"
    st.code(login_url)

auth_code = st.text_input("Paste auth_code here:", type="password")

if st.button("Authenticate") and all([client_id, secret_key, auth_code]):
    try:
        # Generate access token
        url = "https://api.fyers.in/api/v2/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "secret_key": secret_key,
            "redirect_uri": redirect_uri,
            "code": auth_code
        }
        headers = {"content-type": "application/json"}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                access_token = data["access_token"]
                st.success("✅ Authentication successful!")
                st.session_state.access_token = access_token
                st.session_state.client_id = client_id
                
                # Example: Get profile
                profile_url = "https://api.fyers.in/api/v2/profile"
                headers = {"Authorization": f"{client_id}:{access_token}"}
                profile = requests.get(profile_url, headers=headers).json()
                st.write("Profile:", profile)
                
                # Example: Get NIFTY quote
                quote_url = "https://api.fyers.in/data-rest/v2/quotes/"
                params = {"symbols": "NSE:NIFTY50-INDEX"}
                quote = requests.get(quote_url, params=params, headers=headers).json()
                st.write("NIFTY Quote:", quote)
            else:
                st.error(f"Error: {data}")
        else:
            st.error(f"HTTP Error: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")
