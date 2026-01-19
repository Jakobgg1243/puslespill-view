import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from streamlit_javascript import st_javascript

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
    df = pd.DataFrame(sheet.get_all_records())

    df = df.sort_values("Barcode", ascending=True).reset_index(drop=True)
    return df


df = load_data()

width = st_javascript("window.innerWidth", key="win_width")

if width is None:
    st.info("Laster skjermstørrelse...")
    st.stop()          

is_mobile = width <= 600

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

if is_mobile:
    for _, row in display_df.iterrows():
        with st.container(border=True):
            cols = st.columns([1, 3])   
            with cols[0]:
                if row.get("Bilde1"):
                    st.image(row["Bilde1"], width=120)
            with cols[1]:
                st.markdown(f"**EAN:** {row['Barcode']}")
                st.markdown(f"**Tittel:** {row.get('Tittel','–')}")

else:
    st.dataframe(
        display_df,
        height=700,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Barcode": st.column_config.TextColumn("EAN / Strekkode"),
            "Bilde1": st.column_config.ImageColumn(
                "Bilde 1",
                width="medium",   
                help="Første produktbilde"
            ),
            "Bilde2": st.column_config.ImageColumn(
                "Bilde 2",
                width="medium",
            ),
            "Bilde3": st.column_config.ImageColumn(
                "Bilde 3",
                width="medium",
            ),
        },
    )
