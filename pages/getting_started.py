import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import coco_prompt

st.title("Getting Started")
st.markdown("##### Provision your environment for the lab")

st.markdown("---")

st.markdown("## :material/storage: Step 1: Run the setup script")

st.markdown(
    """
The lab uses a synthetic Air Canada dataset in **`AC_HOL_DB`**. Run the setup script
to create the database, schemas, and tables with intentional data quality issues seeded for you to discover.
"""
)

with st.container(border=True):
    st.markdown(
        """
| Schema | Table | Description |
|--------|-------|-------------|
| `OPERATIONS` | `FLIGHTS` | ~10,050 flight records with intentional DQ issues |
| `OPERATIONS` | `FLIGHT_ROUTES` | 20 Air Canada routes (clean reference data) |
| `BOOKINGS` | `RESERVATIONS` | ~25,000 booking records |
| `LOYALTY` | `AEROPLAN_MEMBERS` | ~5,000 loyalty members |
| `AC_HOL_UAT` | `FLIGHTS` | UAT copy — deliberately imperfect (fewer rows, missing columns) |
"""
    )

st.markdown(
    "Copy the contents of the SQL script found "
    "[here](https://github.com/sfc-gh-snotebaert/ac-coco-hol/blob/main/setup.sql) "
    "and run it in a Snowsight worksheet."
)

st.info(
    "You need ACCOUNTADMIN role (granted by default on trial accounts). "
    "Execution takes about 30 seconds."
)

st.markdown("---")

st.markdown("## :material/explore: Step 2: Explore the lab data")

st.markdown(
    """
Before diving into the sessions, get a feel for the data using natural language.
"""
)

coco_prompt(
    "S.1",
    "Explore the Lab Database",
    "What schemas and tables are in AC_HOL_DB? Give me a one-line description of each table.",
)

with st.expander("Expected output"):
    st.markdown(
        """
CoCo queries `INFORMATION_SCHEMA` and returns a summary similar to:

| Schema | Table | Row Count | Description |
|--------|-------|-----------|-------------|
| OPERATIONS | FLIGHTS | ~10,050 | Flight records with status, delay info |
| OPERATIONS | FLIGHT_ROUTES | 20 | Air Canada routes with distance/duration |
| BOOKINGS | RESERVATIONS | ~25,000 | Passenger booking records |
| LOYALTY | AEROPLAN_MEMBERS | ~5,000 | Loyalty tier and points data |
| AC_HOL_UAT | FLIGHTS | ~9,500 | UAT copy (intentional differences) |
"""
    )

coco_prompt(
    "S.2",
    "Sample a Table",
    "Show me 5 sample rows from @AC_HOL_DB.OPERATIONS.FLIGHTS and describe the schema.",
)

st.success("Environment ready. Navigate to **Session 1** to start the lab.")
