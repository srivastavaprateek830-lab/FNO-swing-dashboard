import streamlit as st

# Securely pull your client ID using the correct label string
DHAN_CLIENT_ID = st.secrets["DHAN_CLIENT_ID"]
DHAN_ACCESS_TOKEN = st.secrets["DHAN_ACCESS_TOKEN"]

# Hardcoded threshold constraints
MIN_DELIVERY_PCT = 40.0
MAX_IV_RANK_FOR_BUYING = 50.0
DAYS_TO_EXPIRY_THRESHOLD = 7

# Core Dhan backend url routing endpoint
DHAN_BASE_URL = "https://dhan.co"
