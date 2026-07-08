import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import coco_prompt, tech_card_row, session_meta

st.title("Session 4: Release Confidence & Validation")
session_meta(
    "~15 min",
    "$release-check skill, DDL-blocking hook, pre-release checklist",
)

st.markdown("---")

st.markdown("## :material/verified: Technologies used in this session")
tech_card_row(
    (
        "extension",
        "CoCo Skills",
        "Build a $release-check command that runs a full pre-release checklist in one prompt",
    ),
    (
        "notifications_active",
        "Snowflake Alerts",
        "Automated DQ alerting using DMF results — fires when a quality check fails",
    ),
    (
        "task_alt",
        "PASS/FAIL Checklists",
        "Structured go/no-go output that gives your team a clear release decision",
    ),
)

st.markdown("---")

st.markdown("### Exercise 4.1 — Build the `$release-check` skill")

with st.container(border=True):
    st.markdown(
        ":material/lightbulb: **Goal:** Create a single command that validates everything "
        "before a PROD release. Any data engineer on your team can run it in 10 seconds."
    )

coco_prompt(
    "4.1",
    "Create the $release-check Skill",
    """\
Create a CoCo skill called 'release-check'.
The skill takes a table name as input and runs a pre-release checklist:
1. Row count — report current count and compare to a baseline if available
2. NULL check — flag any NOT NULL columns that have NULLs
3. Primary key integrity — check for duplicate values on the first column (assume it's the PK)
4. Freshness — check load_date is within the last 24 hours
5. Value range sanity — flag numeric columns with negative values
Output a PASS ✅ / WARN ⚠️ / FAIL ❌ summary table.\
""",
)

st.info("Start a new CoCo conversation after creating the skill to use it.")

coco_prompt(
    "4.2",
    "Run Release Check on FLIGHTS",
    "$release-check AC_HOL_DB.OPERATIONS.FLIGHTS",
)

with st.expander(":material/info: Expected output"):
    st.code(
        """\
Pre-Release Check: AC_HOL_DB.OPERATIONS.FLIGHTS
================================================
✅ PASS  — Row count: 10,050
❌ FAIL  — delay_reason: ~200 NULLs where status = 'DELAYED'
❌ FAIL  — flight_id: 50 duplicate values detected
✅ PASS  — load_date: most recent row < 1 hour ago
✅ PASS  — delay_minutes: no negative values
✅ PASS  — passengers_boarded: no negative values

OVERALL: ❌ FAIL — 2 checks failed. Review before promoting to PROD.\
""",
        language="text",
    )

st.markdown("---")

st.markdown("### Exercise 4.2 — Automate DQ alerting with Snowflake Alerts")

with st.container(border=True):
    st.markdown(
        ":material/notifications_active: **Goal:** Instead of waiting for someone to manually "
        "run `$release-check`, set up a Snowflake Alert that automatically fires when the "
        "`NULL_COUNT` DMF on `delay_reason` detects issues — catching problems as soon as data loads."
    )

coco_prompt(
    "4.3",
    "Create a DQ Alert on DMF Results",
    """\
Create a Snowflake Alert on AC_HOL_DB.OPERATIONS.FLIGHTS that:
1. Checks the NULL_COUNT DMF result on delay_reason every hour
2. Fires when NULL count exceeds 0 on rows where status = 'DELAYED'
3. Uses SYSTEM$SEND_EMAIL to notify the team
Show the CREATE ALERT SQL and how to enable it.\
""",
)

with st.expander(":material/code: SQL CoCo generates"):
    st.code(
        """\
CREATE OR REPLACE ALERT AC_HOL_DB.OPERATIONS.dq_delay_reason_alert
  WAREHOUSE = SNOWADHOC
  SCHEDULE = '60 MINUTE'
  IF (EXISTS (
    SELECT 1
    FROM TABLE(
      AC_HOL_DB.INFORMATION_SCHEMA.DATA_METRIC_FUNCTION_REFERENCES(
        ref_entity_name   => 'AC_HOL_DB.OPERATIONS.FLIGHTS',
        ref_entity_domain => 'TABLE'
      )
    )
    WHERE metric_name = 'NULL_COUNT'
      AND value > 0
  ))
  THEN
    CALL SYSTEM$SEND_EMAIL(
      'EMAIL_INTEGRATION',
      'data-team@aircanada.com',
      'DQ Alert: delay_reason NULLs detected in FLIGHTS',
      'NULL_COUNT on delay_reason exceeded threshold. Run $release-check immediately.'
    );

ALTER ALERT AC_HOL_DB.OPERATIONS.dq_delay_reason_alert RESUME;\
""",
        language="sql",
    )

coco_prompt(
    "4.4",
    "Test the Alert Manually",
    "How do I manually execute and verify the dq_delay_reason_alert I just created?",
)

with st.expander(":material/info: Expected output"):
    st.markdown(
        """
CoCo generates the manual execution command and shows you how to check alert history:

```sql
-- Trigger manually
EXECUTE ALERT AC_HOL_DB.OPERATIONS.dq_delay_reason_alert;

-- Check execution history
SELECT *
FROM TABLE(AC_HOL_DB.INFORMATION_SCHEMA.ALERT_HISTORY(
    scheduled_time_range_start => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
ORDER BY scheduled_time DESC;
```
"""
    )

st.markdown("---")

st.markdown("## :material/lightbulb: Key concepts")
st.markdown(
    """
- **`$release-check` skill** — A parameterized skill that runs your pre-release checklist against any table with a single command
- **Snowflake Alerts** — Scheduled checks that query DMF results and fire actions (email, notification) when conditions are met
- **EXECUTE ALERT** — Triggers an alert immediately for testing without waiting for the schedule
- **Go/no-go gate** — A `$release-check` run produces a clear OVERALL PASS or FAIL, giving the release manager an unambiguous decision signal
"""
)

st.markdown("## :material/menu_book: Domain glossary")
st.markdown(
    """
| Term | Definition |
|------|-----------|
| **CoCo Skill** | Saved instruction set invoked with `$skill-name` in any CoCo conversation |
| **Snowflake Alert** | A Snowflake object that evaluates a SQL condition on a schedule and fires an action |
| **EXECUTE ALERT** | SQL command to trigger an alert immediately, bypassing the schedule |
| **Alert history** | `INFORMATION_SCHEMA.ALERT_HISTORY` — query to see past alert executions and outcomes |
| **Release gate** | An automated checkpoint that must PASS before a pipeline change promotes to PROD |
"""
)

st.markdown("## :material/check_circle: What you built in this session")
st.markdown(
    """
- `$release-check` skill — pre-release PASS/FAIL checklist for any table
- Ran the skill on `FLIGHTS` and discovered the 2 failing checks from Session 2
- `dq_delay_reason_alert` — Snowflake Alert that fires automatically when NULL_COUNT DMF exceeds threshold
- Verified the alert by running `EXECUTE ALERT` and inspecting alert history
"""
)
