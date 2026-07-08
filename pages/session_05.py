import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import coco_prompt, tech_card_row, session_meta

st.title("Session 5: Change Impact Analysis")
session_meta(
    "~10 min",
    "Impact report, migration plan, safe schema evolution",
)

st.markdown("---")

with st.container(border=True):
    st.markdown(
        ":material/notifications: **Scenario:** The engineering team wants to rename "
        "`flight_id` to `flight_number` in `OPERATIONS.FLIGHTS` to align with the new "
        "IATA naming standard. This is a **breaking change**. "
        "Let's find everything that references `flight_id` before touching anything."
    )

st.markdown("## :material/account_tree: Technologies used in this session")
tech_card_row(
    (
        "travel_explore",
        "Codebase Search",
        "CoCo uses Grep and Read tools to scan every file in your project directory",
    ),
    (
        "alt_route",
        "Impact Classification",
        "References classified as SELECT, JOIN key, INSERT/UPDATE, or FK dependency",
    ),
    (
        "moving_beds",
        "Zero-Downtime Migration",
        "Add → populate → validate → drop column sequence avoids breaking live queries",
    ),
)

st.markdown("---")

st.markdown("### Exercise 5.1 — Scan for all references before making any change")

coco_prompt(
    "5.1",
    "Snowflake Object Impact Scan",
    """\
Before we rename flight_id to flight_number in AC_HOL_DB.OPERATIONS.FLIGHTS,
scan all Snowflake objects that reference flight_id: views, stored procedures, tasks,
and dynamic tables in AC_HOL_DB.
Use INFORMATION_SCHEMA and GET_DDL to inspect each object.
Classify each reference as: SELECT (read-only), JOIN key, INSERT/UPDATE (write), or FK dependency.
Output a markdown impact report.\
""",
)

with st.expander(":material/info: Expected output"):
    st.markdown(
        """
CoCo queries `INFORMATION_SCHEMA` and uses `GET_DDL` to inspect dependent objects:

```markdown
# Impact Report: Rename flight_id → flight_number
## Scope: AC_HOL_DB.OPERATIONS.FLIGHTS

| Object | Type | Reference Type | Risk |
|--------|------|----------------|------|
| AC_HOL_DB.AC_HOL_UAT.FLIGHTS | TABLE | Same column name | High — downstream queries will break |
| AC_HOL_DB.BOOKINGS.RESERVATIONS | TABLE | JOIN key (flight_id) | High — booking lookups will fail |

## Summary
- 2 references found across 2 objects
- 2 HIGH risk (join keys that would break)
- Recommended: update all JOINs referencing flight_id before deploying rename
```

**Note:** If your lab has additional views or procedures referencing `flight_id`,
CoCo will also flag those in the report.
"""
    )

st.markdown("---")

st.markdown("### Exercise 5.2 — Assess the impact of dropping a column")

coco_prompt(
    "5.2",
    "Column Drop Impact + Migration Plan",
    """\
If we drop the delay_reason column from AC_HOL_DB.OPERATIONS.FLIGHTS,
what queries in our project would fail? What DMFs reference it?
Generate a safe migration plan: (1) deprecation notice, (2) update references, (3) drop column.\
""",
)

with st.expander(":material/info: Expected output"):
    st.markdown(
        """
CoCo checks:
1. Project files referencing `delay_reason`
2. DMFs attached to the column (attached in Session 2)
3. Generates a 3-step migration plan with SQL for each step

```
Step 1 — Deprecate: Add a comment to all SQL files referencing delay_reason
Step 2 — Update references: Modify regression_test.sql to remove NULL rate check on delay_reason
Step 3 — Remove DMF: ALTER TABLE ... DROP DATA METRIC FUNCTION NULL_COUNT ON (delay_reason)
Step 4 — Drop column: ALTER TABLE ... DROP COLUMN delay_reason
```
"""
    )

st.markdown("---")

st.markdown("### Exercise 5.3 — Generate a safe zero-downtime rename migration")

coco_prompt(
    "5.3",
    "Zero-Downtime Column Rename",
    """\
Generate the complete, zero-downtime migration SQL to rename flight_id to flight_number
in AC_HOL_DB.OPERATIONS.FLIGHTS. Include:
- Add new column flight_number
- Populate it from flight_id
- Update any views that reference flight_id
- Drop old column after validation
Save to sql/migrate_flight_id_rename.sql\
""",
)

with st.expander(":material/lightbulb: Why this matters for Air Canada"):
    st.markdown(
        """
Schema changes in operational data systems can silently break downstream reports,
ML models, and dashboards. CoCo's impact analysis turns a **multi-hour audit**
into a **30-second scan** — and generates the safe migration plan automatically.

This is especially important at Air Canada where:
- Multiple teams query `FLIGHTS` independently (operations, revenue, loyalty)
- DMFs are attached to specific columns — dropping a column removes monitoring
- The UAT regression script (`sql/regression_test.sql`) joins on `flight_id` — it would silently fail
"""
    )

st.markdown("---")

st.markdown("## :material/lightbulb: Key concepts")
st.markdown(
    """
- **Impact scan** — CoCo uses `INFORMATION_SCHEMA` and `GET_DDL` to find every Snowflake object that references a column or table
- **Risk classification** — References are ranked: JOIN key > INSERT/UPDATE > SELECT — each has a different fix complexity
- **Zero-downtime rename** — Add new column → populate from old → update dependent objects → drop old column; live queries never break
- **DMF awareness** — CoCo knows to include DMF removal in the migration plan so monitoring doesn't silently disappear
"""
)

st.markdown("## :material/menu_book: Domain glossary")
st.markdown(
    """
| Term | Definition |
|------|-----------|
| **Impact analysis** | Scanning all code and configuration to find what would break if a change is made |
| **Breaking change** | A schema modification that causes existing queries or pipelines to fail |
| **Zero-downtime migration** | A change pattern that never leaves the system in an inconsistent state |
| **FK dependency** | A foreign key relationship where another table's column references this one |
| **IATA** | International Air Transport Association — sets global aviation data standards |
"""
)

st.markdown("## :material/check_circle: What you built in this session")
st.markdown(
    """
- `reports/impact_flight_id_rename.md` — full impact report with risk classification across Snowflake objects
- Assessed the consequences of dropping `delay_reason` including DMF removal
- `sql/migrate_flight_id_rename.sql` — zero-downtime migration script for `flight_id → flight_number`
"""
)
