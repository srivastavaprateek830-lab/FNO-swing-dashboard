import streamlit as st

# Securely extract production routing credentials straight from Streamlit secrets
DHAN_CLIENT_ID = st.secrets["1100533176"]
DHAN_ACCESS_TOKEN = st.secrets["aa70b48b-473a-464d-b133-361d953f87aa"]

# Fixed strategy parameter boundaries
MIN_DELIVERY_PCT = 40.0
MAX_IV_RANK_FOR_BUYING = 50.0
DAYS_TO_EXPIRY_THRESHOLD = 7

# Official DhanHQ Production OpenAPI Core Endpoints
DHAN_BASE_URL = "https://dhan.co"
