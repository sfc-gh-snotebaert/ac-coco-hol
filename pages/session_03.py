import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import coco_prompt, tech_card_row, session_meta

st.title("Session 3: Non-Regression Testing (UAT → PROD)")
session_meta(
    "~20 min",
    "regression_test.sql, AGENTS.md project governance rules",
)

st.markdown("---")

with st.container(border=True):
    st.markdown(
        ":material/info: **Lab context:** `AC_HOL_DB.AC_HOL_UAT.FLIGHTS` is a deliberately imperfect copy of PROD: "
        "**2 columns removed** (`aircraft_type`, `delay_reason`) and **~550 fewer rows**. "
        "Your job is to catch these issues before they reach production."
    )

st.markdown("## :material/compare_arrows: Technologies used in this session")
tech_card_row(
    (
        "difference",
        "Schema Comparison",
        "Compare INFORMATION_SCHEMA.COLUMNS across environments to catch column drift",
    ),
    (
        "table_rows",
        "SQL Assertion Scripts",
        "CASE-based PASS/FAIL checks with tolerance thresholds",
    ),
    (
        "policy",
        "AGENTS.md Rules",
        "Project-level governance instructions CoCo follows automatically every session",
    ),
)

st.markdown("---")

st.markdown("### Exercise 3.1 — Automated UAT vs PROD comparison")

coco_prompt(
    "3.1",
    "Compare PROD and UAT Environments",
    """\
Compare AC_HOL_DB.OPERATIONS.FLIGHTS (PROD) with AC_HOL_DB.AC_HOL_UAT.FLIGHTS (UAT).
Check:
1. Schema differences — which columns exist in PROD but not UAT (or vice versa)?
2. Row count difference
3. Aggregate consistency: total delay_minutes, cancellation rate, average passengers_boarded
4. Status distribution — does the % of DELAYED flights match between environments?
Output a comparison table and flag each check as PASS or FAIL.\
""",
)

with st.expander(":material/warning: Issues CoCo should flag"):
    st.markdown(
        """
| Check | PROD | UAT | Result |
|-------|------|-----|--------|
| Row count | ~10,050 | ~9,500 | ❌ FAIL — 550 row gap |
| Columns | 14 | 12 | ❌ FAIL — missing `aircraft_type`, `delay_reason` |
| Cancellation rate | ~3% | ~3% | ✅ PASS |
| Avg delay_minutes | ~62 | ~61 | ✅ PASS |

CoCo queries `INFORMATION_SCHEMA.COLUMNS` for schema diffs and runs aggregates on both tables.
"""
    )

st.markdown("---")

st.markdown("### Exercise 3.2 — Generate a reusable regression test script")

coco_prompt(
    "3.2",
    "Generate regression_test.sql",
    """\
Generate a SQL regression test script called regression_test.sql that I can run
before every release to compare AC_HOL_DB.AC_HOL_UAT.FLIGHTS with AC_HOL_DB.OPERATIONS.FLIGHTS.
The script should:
- Use CASE-based checks that display PASS or FAIL for each assertion
- Check: row count within 1% tolerance, column schema matches, NULL rates within 2%,
  status distribution within 3%, no new unexpected status values
- Print PASS/FAIL for each check
Save the script as regression_test.sql\
""",
)

with st.expander(":material/code: Expected script pattern"):
    st.code(
        """\
-- regression_test.sql
-- Air Canada UAT → PROD regression checks
-- Run before every pipeline release

SET prod_count = (SELECT COUNT(*) FROM AC_HOL_DB.OPERATIONS.FLIGHTS);
SET uat_count  = (SELECT COUNT(*) FROM AC_HOL_DB.AC_HOL_UAT.FLIGHTS);

-- Check 1: Row count within 1% tolerance
SELECT
    CASE
        WHEN ABS($prod_count - $uat_count) / $prod_count::FLOAT < 0.01
        THEN 'PASS: Row counts within 1% tolerance'
        ELSE 'FAIL: Row count gap = ' || ABS($prod_count - $uat_count)::VARCHAR
    END AS row_count_check;

-- Check 2: Schema columns match
SELECT
    column_name,
    CASE WHEN uat.column_name IS NULL THEN 'MISSING IN UAT' ELSE 'PRESENT' END AS status
FROM (
    SELECT column_name FROM AC_HOL_DB.INFORMATION_SCHEMA.COLUMNS
    WHERE table_schema = 'OPERATIONS' AND table_name = 'FLIGHTS'
) prod
LEFT JOIN (
    SELECT column_name FROM AC_HOL_DB.INFORMATION_SCHEMA.COLUMNS
    WHERE table_schema = 'AC_HOL_UAT' AND table_name = 'FLIGHTS'
) uat USING (column_name);\
""",
        language="sql",
    )

st.markdown("---")

st.markdown("### Exercise 3.3 — Enforce release standards with AGENTS.md")

with st.container(border=True):
    st.markdown(
        ":material/description: **About AGENTS.md:** This is a project-level instruction file "
        "that CoCo reads at the start of every session. It's how you encode team standards so "
        "CoCo follows them automatically — no need to repeat rules in every prompt."
    )

coco_prompt(
    "3.3",
    "Create Project Governance Rules",
    """\
Create an AGENTS.md file for this CoCo session with these Air Canada data governance rules:
1. Always compare UAT vs PROD row counts before any data migration or pipeline deployment
2. Never run INSERT, UPDATE, or DELETE on OPERATIONS or BOOKINGS schemas without explicit user confirmation
3. Always include schema name prefix when referencing tables (never bare table names)
4. All new SQL files must go in the sql/ directory and include a comment header with: author, date, purpose
5. Before dropping any column, run the change impact analysis skill\
""",
)

coco_prompt(
    "3.4",
    "Test a Governance Rule",
    "Insert 10 test rows into AC_HOL_DB.OPERATIONS.FLIGHTS with dummy data.",
)

with st.expander(":material/info: Expected behavior"):
    st.markdown(
        """
Because of **Rule 2** in `AGENTS.md`, CoCo should **pause and ask for explicit confirmation**
before executing the `INSERT`:

> _"This INSERT targets the OPERATIONS schema. Per project rules, I need your explicit
> confirmation before modifying this schema. Should I proceed?"_

Type **no** to see the block in action. Type **yes** to allow it.
"""
    )

st.markdown("---")

st.markdown("## :material/lightbulb: Key concepts")
st.markdown(
    """
- **Schema comparison** — Querying `INFORMATION_SCHEMA.COLUMNS` across two environments reveals column drift before it causes runtime errors
- **SQL assertions** — `CASE` statements with tolerance thresholds (`< 0.01` for row count, etc.) produce human-readable PASS/FAIL output without raising exceptions
- **AGENTS.md** — Loaded at the start of each CoCo conversation; enforces team conventions automatically
- **Rule-based blocking** — CoCo respects explicit "never" rules and asks for confirmation rather than proceeding silently
"""
)

st.markdown("## :material/menu_book: Domain glossary")
st.markdown(
    """
| Term | Definition |
|------|-----------|
| **UAT** | User Acceptance Testing — a staging environment that mirrors PROD |
| **PROD** | Production — the live environment serving real airline operations |
| **Schema drift** | When the column structure of a table changes unexpectedly between environments |
| **Tolerance threshold** | An acceptable margin of variance (e.g., row count within 1%) that avoids false alarms |
| **AGENTS.md** | A project instruction file read by CoCo on startup to enforce team conventions |
"""
)

st.markdown("## :material/check_circle: What you built in this session")
st.markdown(
    """
- Automated PROD vs UAT comparison that surfaces schema drift and row count gaps
- `sql/regression_test.sql` — reusable pre-release assertion script
- `AGENTS.md` with 5 Air Canada data governance rules
- Verified that AGENTS.md rules are enforced on the very next CoCo prompt
"""
)
