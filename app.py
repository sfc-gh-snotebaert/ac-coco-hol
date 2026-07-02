import streamlit as st

st.set_page_config(
    page_title="Air Canada × CoCo — Hands-On Lab",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.logo(
    "https://upload.wikimedia.org/wikipedia/commons/f/ff/Snowflake_Logo.svg",
    link="https://www.snowflake.com",
    size="large",
)

pg = st.navigation(
    {
        "": [
            st.Page("pages/home.py", title="Home", icon=":material/home:"),
            st.Page("pages/getting_started.py", title="Getting Started", icon=":material/rocket_launch:"),
        ],
        "Lab Sessions": [
            st.Page("pages/session_01.py", title="1. Data Discovery", icon=":material/search:"),
            st.Page("pages/session_02.py", title="2. DQ Rules", icon=":material/rule:"),
            st.Page("pages/session_03.py", title="3. Non-Regression Testing", icon=":material/compare_arrows:"),
            st.Page("pages/session_04.py", title="4. Release Confidence", icon=":material/verified:"),
            st.Page("pages/session_05.py", title="5. Change Impact", icon=":material/account_tree:"),
            st.Page("pages/wrap_up.py", title="Wrap-Up", icon=":material/emoji_events:"),
        ],
    }
)

pg.run()
