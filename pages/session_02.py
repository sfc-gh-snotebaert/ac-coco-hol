import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import coco_prompt, tech_card_row, session_meta

st.title("Session 2: Data Quality Rule Generation")
session_meta(
    "~20 min",
    "$profile-ac-table skill, Data Metric Functions, automated DQ monitoring",
)

st.markdown("---")

st.markdown("## :material/rule: Technologies used in this session")
tech_card_row(
    (
        "query_stats",
        "Table Profiling",
        "NULL counts, duplicate detection, value range checks via CoCo",
    ),
    (
        "monitoring",
        "Data Metric Functions",
        "Snowflake's built-in NULL_COUNT, DUPLICATE_COUNT, FRESHNESS DMFs",
    ),
    (
        "extension",
        "Custom CoCo Skills",
        "Save reusable profiling logic as a $skill anyone on the team can invoke",
    ),
)

st.markdown("---")

st.markdown("### Exercise 2.1 — Profile a table and discover hidden DQ issues")

with st.container(border=True):
    st.markdown(
        ":material/notifications: **Scenario:** Before the Q3 release, someone on your team "
        "suspects the `FLIGHTS` table has missing delay reasons. Let's find out."
    )

coco_prompt(
    "2.1",
    "Profile the FLIGHTS Table",
    """\
Profile AC_HOL_DB.OPERATIONS.FLIGHTS. For each column, check:
- NULL count and percentage
- Duplicate values on flight_id
- Any numeric columns with suspicious values (negatives, zeros in key fields)
- Row count and date range of scheduled_departure
Present results as a markdown summary.\
""",
)

with st.expander(":material/warning: Issues CoCo should find"):
    st.markdown(
        """
| Column | Issue | Count |
|--------|-------|-------|
| `delay_reason` | NULL where `status = 'DELAYED'` | ~200 rows |
| `flight_id` | Duplicate values | ~50 rows |
| `delay_minutes` | NULL where `status = 'CANCELLED'` | Expected — valid |

CoCo flags the `delay_reason` NULLs on DELAYED flights as a **data quality issue**
(not just missing optionals), because it reads business context from column names.
"""
    )

coco_prompt(
    "2.2",
    "Profile the LOYALTY Table",
    """\
Profile AC_HOL_DB.LOYALTY.AEROPLAN_MEMBERS.
Focus on: points_balance (are there negative values?), member_since date range,
tier distribution, and any NULL preferred_seat patterns.\
""",
)

with st.expander(":material/warning: Issues CoCo should find"):
    st.markdown(
        """
CoCo finds **~30 rows with negative `points_balance`** — a business impossibility.
These were injected as a realistic pipeline bug (e.g., a reversed delta calculation).

Also expect: NULL `preferred_seat` on ~17% of rows — borderline acceptable.
"""
    )

st.markdown("---")

st.markdown("### Exercise 2.2 — Generate Data Metric Functions (DMFs)")

with st.container(border=True):
    st.markdown(
        ":material/lightbulb: **Context:** Now that we know what to monitor, tell CoCo to "
        "generate and attach DMFs so these checks run automatically on every pipeline refresh."
    )

coco_prompt(
    "2.3",
    "Generate and Attach DMFs to FLIGHTS",
    """\
Generate Snowflake Data Metric Functions to monitor AC_HOL_DB.OPERATIONS.FLIGHTS:
1. NULL count on delay_reason
2. Duplicate count on flight_id
3. Freshness check on load_date (flag if no data loaded in last 25 hours)
Attach them to the table with TRIGGER_ON_CHANGES schedule. Show the SQL.\
""",
)

with st.expander(":material/code: SQL CoCo generates"):
    st.code(
        """\
ALTER TABLE AC_HOL_DB.OPERATIONS.FLIGHTS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (delay_reason)
  SCHEDULE = 'TRIGGER_ON_CHANGES';

ALTER TABLE AC_HOL_DB.OPERATIONS.FLIGHTS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.DUPLICATE_COUNT ON (flight_id)
  SCHEDULE = 'TRIGGER_ON_CHANGES';

ALTER TABLE AC_HOL_DB.OPERATIONS.FLIGHTS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.FRESHNESS ON (load_date)
  SCHEDULE = 'TRIGGER_ON_CHANGES';\
""",
        language="sql",
    )

st.markdown("---")

st.markdown("### Exercise 2.3 — Build a reusable table-profiling skill")

with st.container(border=True):
    st.markdown(
        ":material/extension: **Goal:** Create a `$profile-ac-table` skill that anyone on the "
        "team can run in one command to audit any table before a release."
    )

coco_prompt(
    "2.4",
    "Create the $profile-ac-table Skill",
    """\
Create a custom CoCo skill called 'profile-ac-table' that:
1. Takes a fully qualified table name as input
2. Counts rows and checks date range of any TIMESTAMP columns
3. Reports NULL % for every column
4. Flags numeric columns with negative values
5. Checks for duplicate primary key candidates
6. Outputs a PASS/WARN/FAIL status per check
Save the skill so CoCo can use it.
""",
)

st.info(
    "**After CoCo creates the skill:** start a new CoCo conversation to load it."
)

coco_prompt(
    "2.5",
    "Test the Skill on RESERVATIONS",
    "$profile-ac-table AC_HOL_DB.BOOKINGS.RESERVATIONS",
)

with st.expander(":material/info: Expected output"):
    st.code(
        """\
Table: AC_HOL_DB.BOOKINGS.RESERVATIONS (25,000 rows)
✅ PASS  — No duplicate booking_id
⚠️ WARN  — cabin_class: 0.4% NULLs (100 rows)
✅ PASS  — ticket_price: no negative values
✅ PASS  — booking_date: range 2023-07-01 to 2024-07-01\
""",
        language="text",
    )

st.markdown("---")

st.markdown("## :material/lightbulb: Key concepts")
st.markdown(
    """
- **Data Metric Functions (DMFs)** — Snowflake built-ins (`NULL_COUNT`, `DUPLICATE_COUNT`, `FRESHNESS`) that attach to tables and run on a schedule
- **TRIGGER_ON_CHANGES** — DMF schedule that re-runs checks only when the table data changes (most efficient)
- **Custom skills** — Saved in `.cortex/skills/<name>/SKILL.md`; loaded on CoCo startup; invoked with `$skill-name`
- **Proactive profiling** — Run `$profile-ac-table` before every release to catch regressions early
"""
)

st.markdown("## :material/menu_book: Domain glossary")
st.markdown(
    """
| Term | Definition |
|------|-----------|
| **DMF** | Data Metric Function — a Snowflake object that measures a data quality metric on a table |
| **NULL_COUNT** | Built-in DMF: counts NULL values in a specified column |
| **DUPLICATE_COUNT** | Built-in DMF: counts rows with non-unique values in a specified column |
| **FRESHNESS** | Built-in DMF: measures elapsed time since the most recent row was inserted |
| **Skill** | A saved CoCo instruction set that becomes a reusable `$command` |
"""
)

st.markdown("## :material/check_circle: What you built in this session")
st.markdown(
    """
- Profiled `FLIGHTS` and `LOYALTY.AEROPLAN_MEMBERS` tables — discovered real DQ issues
- Generated SQL to attach `NULL_COUNT`, `DUPLICATE_COUNT`, and `FRESHNESS` DMFs to `FLIGHTS`
- Created the `$profile-ac-table` custom skill
- Tested the skill against `BOOKINGS.RESERVATIONS`
"""
)
