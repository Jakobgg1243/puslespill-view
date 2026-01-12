import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Puslespill View", layout="wide")
st.title("Puslespill View")

creds_info = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(
    creds_info, 
    scopes=[
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
)

@st.cache_data(ttl=60)
def load_data():
    client = gspread.authorize(creds)
    sheet = client.open("Puslespill").sheet1
    return pd.DataFrame(sheet.get_all_records())

df = load_data()

search_query = st.text_input(
    "Søk etter strekkode (EAN)",
    value="",
    placeholder="Skriv her f.eks. 7045952001235",
    help="Skriv inn hele eller deler av EAN-nummeret (13 siffer)",
    key="ean_search",
).strip()

if search_query:
    mask = df["Barcode"].astype(str).str.startswith(search_query)

    filtered_df = df[mask]

    if filtered_df.empty:
        st.warning(f"Ingen treff for '{search_query}'")
    else:
        st.success(f"Fant {len(filtered_df)} treff")
    display_df = filtered_df
else:
    display_df = df
    st.info(f"Totalt {len(display_df)} puslespill i listen")
    
st.write("Data lastet fra Google Sheets:")
st.dataframe(
    display_df,
    height=700,
    hide_index=True,
    width="stretch",
    column_config={
        "Barcode": st.column_config.TextColumn("EAN / Strekkode"),
        "Bilde1": st.column_config.ImageColumn(
            "Bilde 1",
            width="auto",
            help="Første produktbilde"
        ),
        "Bilde2": st.column_config.ImageColumn(
            "Bilde 2",
            width="auto",
        ),
        "Bilde3": st.column_config.ImageColumn(
            "Bilde 3",
            width="auto",
        ),
    },
)

