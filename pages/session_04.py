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
        "webhook",
        "CoCo Hooks",
        "PreToolUse hooks intercept tool calls before execution — block dangerous DDL automatically",
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
Create a CoCo skill called 'release-check' saved to .cortex/skills/release-check/SKILL.md.
The skill takes a table name as input and runs a pre-release checklist:
1. Row count — report current count and compare to a baseline if available
2. NULL check — flag any NOT NULL columns that have NULLs
3. Primary key integrity — check for duplicate values on the first column (assume it's the PK)
4. Freshness — check load_date is within the last 24 hours
5. Value range sanity — flag numeric columns with negative values
Output a PASS ✅ / WARN ⚠️ / FAIL ❌ summary table.\
""",
)

st.info("Restart your CoCo session after creating the skill to load it.")

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
❌ FAIL  — delay_reason: 198 NULLs where status = 'DELAYED'
❌ FAIL  — flight_id: 50 duplicate values detected
✅ PASS  — load_date: most recent row < 1 hour ago
✅ PASS  — delay_minutes: no negative values
✅ PASS  — passengers_boarded: no negative values

OVERALL: ❌ FAIL — 2 checks failed. Review before promoting to PROD.\
""",
        language="text",
    )

st.markdown("---")

st.markdown("### Exercise 4.2 — Block dangerous DDL with a hook")

with st.container(border=True):
    st.markdown(
        ":material/webhook: **About hooks:** A CoCo hook is a shell script that runs "
        "before or after a tool is executed. A `PreToolUse` hook can inspect the incoming "
        "tool call and block it (exit code 2) before any damage is done."
    )

coco_prompt(
    "4.3",
    "Create a DDL-Blocking Hook",
    """\
Create a CoCo hook that blocks any SQL containing DROP, ALTER TABLE, TRUNCATE, or CREATE TABLE
against AC_HOL_DB.OPERATIONS or AC_HOL_DB.BOOKINGS schemas.
The hook should print a clear error message and log the blocked attempt to /tmp/coco_blocked.log.
Save the hook to hooks/block-prod-ddl.sh and register it in hooks.json.\
""",
)

with st.expander(":material/code: Hook script CoCo generates"):
    st.code(
        """\
#!/bin/bash
INPUT=$(cat)
TOOL=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)

if [ "$TOOL" = "snowflake_sql_execute" ]; then
    SQL=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('sql','').upper())" 2>/dev/null)

    if echo "$SQL" | grep -qE "(DROP|ALTER TABLE|TRUNCATE|CREATE TABLE).*(OPERATIONS|BOOKINGS)"; then
        MSG="BLOCKED: DDL against OPERATIONS/BOOKINGS schemas requires a change request."
        echo "$MSG" >&2
        echo "$(date): $MSG | SQL: $SQL" >> /tmp/coco_blocked.log
        exit 2
    fi
fi
exit 0\
""",
        language="bash",
    )

coco_prompt(
    "4.4",
    "Test the Hook",
    "Drop the delay_reason column from AC_HOL_DB.OPERATIONS.FLIGHTS.",
)

with st.expander(":material/info: Expected behavior"):
    st.markdown(
        """
The hook intercepts the `snowflake_sql_execute` call and returns exit code 2, which CoCo
treats as a hard block. You should see:

```
Hook blocked: BLOCKED: DDL against OPERATIONS/BOOKINGS schemas requires a change request.
```

Check `/tmp/coco_blocked.log` to confirm the attempt was logged.
"""
    )

st.markdown("---")

st.markdown("## :material/lightbulb: Key concepts")
st.markdown(
    """
- **`$release-check` skill** — A parameterized skill that runs your pre-release checklist against any table with a single command
- **PreToolUse hooks** — Shell scripts that run before CoCo executes a tool; exit code 2 = hard block with message; exit code 1 = soft warning
- **hooks.json** — Located in `~/.snowflake/cortex/hooks/`; registers which hooks run on which tool events
- **Go/no-go gate** — A `$release-check` run produces a clear OVERALL PASS or FAIL, giving the release manager an unambiguous decision signal
"""
)

st.markdown("## :material/menu_book: Domain glossary")
st.markdown(
    """
| Term | Definition |
|------|-----------|
| **CoCo Skill** | Saved instruction set in `.cortex/skills/<name>/SKILL.md`; invoked with `$skill-name` |
| **Hook** | Shell script that intercepts CoCo tool calls; registered in `hooks.json` |
| **PreToolUse** | Hook event that fires before a tool executes — can block or modify the call |
| **Exit code 2** | Hard block — CoCo stops execution and displays the hook's error message to the user |
| **Release gate** | An automated checkpoint that must PASS before a pipeline change promotes to PROD |
"""
)

st.markdown("## :material/check_circle: What you built in this session")
st.markdown(
    """
- `$release-check` skill — pre-release PASS/FAIL checklist for any table
- Ran the skill on `FLIGHTS` and discovered the 2 failing checks from Session 2
- `hooks/block-prod-ddl.sh` — DDL protection hook with audit logging
- Verified the hook blocks a DROP COLUMN attempt in real time
"""
)
