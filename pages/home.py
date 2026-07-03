import streamlit as st

st.title("Air Canada × Snowflake Cortex Code")
st.markdown("##### Data Quality, Testing & Impact Analysis — 90-Minute Hands-On Lab")

st.markdown("")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Sessions", "5")
with col2:
    st.metric("Prompts", "15+")
with col3:
    st.metric("Duration", "~90 min", help="Total estimated lab time")
with col4:
    st.metric("Tables", "4 + UAT")

st.markdown("---")

st.markdown("## How this workshop works")
st.markdown(
    """
Each session has **numbered prompts** that you copy and paste directly into **Cortex Code (CoCo)**.
CoCo interprets your natural language instruction and executes the appropriate SQL, Python, or
configuration against your Snowflake account.

- Sessions build on each other — complete them in order
- Prompts are designed to surface **real data quality issues** seeded into the lab data
- By the end you'll have reusable **skills**, **hooks**, and **test scripts** your team can adopt today
"""
)

st.markdown("## :material/flight_takeoff: The scenario")
st.markdown(
    """
Air Canada's analytics team is preparing the **Q3 release** of their passenger operations
pipeline. Before this release goes to production, the team must:

- Validate data quality across flight operations, bookings, and loyalty tables
- Run regression tests comparing UAT and PROD environments
- Assess the impact of a planned schema change to the `FLIGHTS` table
- Build reusable CoCo skills the team can use every sprint

You are a **data engineer** on this team. **Cortex Code** is your AI-powered assistant
running directly in **Snowsight**.
"""
)

st.markdown("## :material/construction: What we're building")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("**Artifacts you'll create**")
        st.markdown(
            """
- `$profile-ac-table` — reusable table profiler skill
- `$release-check` — pre-release validation checklist skill
- `sql/regression_test.sql` — automated UAT vs PROD test suite
- `AGENTS.md` — project governance rules
- `dq_delay_reason_alert` — automated DQ alert on NULL_COUNT DMF
- `reports/impact_flight_id_rename.md` — change impact report
"""
        )

with col2:
    with st.container(border=True):
        st.markdown("**Lab objectives**")
        st.markdown(
            """
1. :material/search: Drive faster data discovery and analytics enablement
2. :material/rule: Accelerate data quality rule generation
3. :material/compare_arrows: Improve non-regression testing (UAT/PROD)
4. :material/verified: Strengthen data validation and release confidence
5. :material/account_tree: Enable change impact analysis
"""
        )

st.markdown("---")

st.markdown("## :material/checklist: Prerequisites")
st.markdown(
    """
The only prerequisite for this lab is a **Snowflake trial account** in the **AWS US West** region.

[Sign up for a free Snowflake trial →](https://trial.snowflake.com)

The **Getting Started** page walks through environment setup step by step.
"""
)
