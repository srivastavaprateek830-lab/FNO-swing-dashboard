import streamlit as st

# Securely fetch credentials from Streamlit Cloud Secrets
DHAN_CLIENT_ID = st.secrets["DHAN_CLIENT_ID"]
DHAN_ACCESS_TOKEN = st.secrets["DHAN_ACCESS_TOKEN"]

# Parameter Thresholds
MIN_DELIVERY_PCT = 40.0
MAX_IV_RANK_FOR_BUYING = 50.0
DAYS_TO_EXPIRY_THRESHOLD = 7

# Core Infrastructure Endpoints
DHAN_BASE_URL = "https://dhan.co"
