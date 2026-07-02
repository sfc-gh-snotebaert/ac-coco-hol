import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import coco_prompt, tech_card_row, session_meta

st.title("Session 1: Data Discovery & Analytics Enablement")
session_meta(
    "~15 min",
    "SQL queries, business insights, $sql-author skill",
)

st.markdown("---")

st.markdown("## :material/search: Technologies used in this session")
tech_card_row(
    (
        "manage_search",
        "Natural Language SQL",
        "Ask business questions without knowing the exact column names",
    ),
    (
        "schema",
        "Schema Context (#DB.S.T)",
        "CoCo reads INFORMATION_SCHEMA to understand table structure in real-time",
    ),
    (
        "terminal",
        "$sql-author Skill",
        "Generate clean, commented SQL with best-practice patterns",
    ),
)

st.markdown("---")

st.markdown("### Exercise 1.1 — Answer a business question without knowing the table structure")

with st.container(border=True):
    st.markdown(
        ":material/notifications: **Scenario:** The operations manager just asked: "
        "_'How did our on-time performance look last quarter by departure hub?'_ "
        "You don't know the exact column names — just ask CoCo."
    )

coco_prompt(
    "1.1",
    "On-Time Performance by Hub",
    """\
How many flights were ON_TIME vs DELAYED vs CANCELLED in AC_HOL_DB in the last 90 days?
Break it down by departure_airport. Show the delay rate as a percentage.\
""",
)

with st.expander(":material/info: Expected output"):
    st.markdown(
        """
CoCo identifies the `FLIGHTS` table, builds a `GROUP BY` query, executes it, and returns
a table like:

| departure_airport | ON_TIME | DELAYED | CANCELLED | delay_rate_pct |
|---|---|---|---|---|
| YYZ | 4,812 | 1,247 | 203 | 19.7% |
| YVR | … | … | … | … |

Notice: CoCo inferred the date column (`scheduled_departure`) from schema context alone.
"""
    )

coco_prompt(
    "1.2",
    "Worst Delay Routes",
    """\
Which 10 routes have the highest average delay in minutes?
Only include routes with at least 50 delayed flights.\
""",
)

with st.expander(":material/info: Expected output"):
    st.markdown(
        """
CoCo joins on departure + arrival airports, filters `status = 'DELAYED'`,
applies `HAVING COUNT(*) >= 50`, and orders by `AVG(delay_minutes) DESC`.
"""
    )

st.markdown("---")

st.markdown("### Exercise 1.2 — SQL authoring with the `$sql-author` skill")

with st.container(border=True):
    st.markdown(
        ":material/lightbulb: **Context:** The revenue team wants a load factor report. "
        "Load factor = `passengers_boarded / capacity`. Use the `$sql-author` skill to produce "
        "a clean, well-commented query."
    )

coco_prompt(
    "1.3",
    "Load Factor Analysis",
    """\
$sql-author Write a query to calculate load factor (passengers_boarded / capacity)
by aircraft_type and route (departure_airport + arrival_airport).
Include average ticket revenue per seat from BOOKINGS.RESERVATIONS.
Sort by load factor descending.\
""",
)

with st.expander(":material/info: Expected output"):
    st.markdown(
        """
CoCo generates a clean SQL query with:
- A `JOIN` between `FLIGHTS` and `RESERVATIONS` on `flight_id`
- `AVG(passengers_boarded::FLOAT / NULLIF(capacity, 0))` for safe division
- Revenue aggregated from bookings
- A comment header explaining the query purpose

You can copy this to a `.sql` file or run it directly in Snowsight.
"""
    )

coco_prompt(
    "1.4",
    "Loyalty Engagement Analysis",
    """\
How many Aeroplan members in AC_HOL_DB booked at least one flight in the last 6 months?
Break down by loyalty tier (SUPER_ELITE, ALTITUDE_75K, etc.).\
""",
)

with st.expander(":material/info: What to notice"):
    st.markdown(
        """
CoCo must join `LOYALTY.AEROPLAN_MEMBERS` with `BOOKINGS.RESERVATIONS`.
Notice how it resolves the join key (`customer_id`) by reading both schemas —
without you specifying it.
"""
    )

st.markdown("---")

st.markdown("## :material/lightbulb: Key concepts")
st.markdown(
    """
- **Schema context** — CoCo reads `INFORMATION_SCHEMA` automatically when you reference a table with `#DB.SCHEMA.TABLE`
- **Natural language SQL** — No need to remember column names; describe the business question and CoCo writes the SQL
- **`$sql-author` skill** — Produces annotated, production-ready SQL with comments, safe division guards, and formatting conventions
- **Prompt refinement** — If the first result isn't what you need, add constraints in the next turn ("only include routes with at least 50 flights")
"""
)

st.markdown("## :material/menu_book: Domain glossary")
st.markdown(
    """
| Term | Definition |
|------|-----------|
| **OTP (On-Time Performance)** | % of flights that depart or arrive within 15 minutes of schedule |
| **Load factor** | `passengers_boarded / capacity` — measures how full flights are |
| **Delay reason** | Categorical code explaining a delay (e.g., weather, mechanical, crew) |
| **Aeroplan tier** | Air Canada's loyalty tiers: Standard → 25K → 35K → 50K → 75K → Super Elite |
| **Hub** | A major airport serving as a connection point (YYZ = Toronto, YVR = Vancouver) |
"""
)

st.markdown("## :material/check_circle: What you built in this session")
st.markdown(
    """
- On-time performance query broken down by hub
- Worst-delay routes with minimum flight volume filter
- Load factor analysis joined across `FLIGHTS` and `RESERVATIONS`
- Loyalty booking engagement report with tier breakdown
"""
)
