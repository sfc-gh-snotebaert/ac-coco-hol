import streamlit as st


def coco_prompt(number: str, title: str, text: str):
    """Render a CoCo prompt block matching port-hol.streamlit.app style."""
    st.markdown(f"### :material/terminal: Prompt {number} — {title}")
    st.caption("Copy this prompt and paste it into Cortex Code")
    st.code(text.strip(), language="text")


def tech_card_row(*cards):
    """Render a row of bordered tech cards. Each card: (icon, title, description)."""
    cols = st.columns(len(cards))
    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            with st.container(border=True):
                st.markdown(f"**:material/{icon}: {title}**")
                st.caption(desc)


def session_meta(duration: str, building: str):
    """Render the time + building metadata row under a session title."""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f":material/schedule: {duration}")
    with col2:
        st.markdown(f":material/build: **Building:** {building}")
