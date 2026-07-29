import streamlit as st
import os


def _get_secret(key: str, default=None):
    """Reads a secret from Streamlit's secrets manager first, then env vars.
    Never hardcode real credentials in this file - it gets committed to git."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


DHAN_CLIENT_ID = _get_secret("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = _get_secret("DHAN_ACCESS_TOKEN")

if not DHAN_CLIENT_ID or not DHAN_ACCESS_TOKEN:
    st.error(
        "⚠️ Dhan credentials are missing. Add DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN "
        "in Streamlit Cloud → App settings → Secrets (see setup notes)."
    )
    st.stop()

# Hardcoded strategy thresholds
MIN_DELIVERY_PCT = 40.0
MAX_IV_RANK_FOR_BUYING = 50.0
DAYS_TO_EXPIRY_THRESHOLD = 7

# Real DhanHQ v2 API host (dhan.co is just the marketing website, not the API)
DHAN_BASE_URL = "https://api.dhan.co"
