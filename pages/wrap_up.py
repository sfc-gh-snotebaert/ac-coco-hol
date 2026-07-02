import streamlit as st

st.title("Wrap-Up & Key Takeaways")
st.markdown("##### You've completed the Air Canada × Snowflake Cortex Code Hands-On Lab")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### :material/build: What you built")
        st.markdown(
            """
- `$profile-ac-table` — reusable table profiler skill
- `$release-check` — pre-release validation checklist skill
- `sql/regression_test.sql` — automated UAT vs PROD test suite
- `AGENTS.md` — project governance rules (5 enforced conventions)
- `hooks/block-prod-ddl.sh` — DDL protection for PROD schemas
- `reports/impact_flight_id_rename.md` — change impact report
- `sql/migrate_flight_id_rename.sql` — zero-downtime migration script
"""
        )

with col2:
    with st.container(border=True):
        st.markdown("### :material/swap_horiz: CoCo capability → Air Canada use case")
        st.markdown(
            """
| Capability | Air Canada Use Case |
|---|---|
| Natural language SQL | Instant ad-hoc flight/booking queries |
| `$sql-author` skill | Faster SQL authoring for analysts |
| DMF generation | Automated DQ on every pipeline load |
| Schema comparison | UAT vs PROD regression gating |
| `$release-check` skill | Go/no-go decision in 10 seconds |
| Hooks | Block DDL accidents in PROD |
| Impact analysis | Safe schema evolution before release |
| `AGENTS.md` rules | Team standards enforced automatically |
"""
        )

st.markdown("---")

st.markdown("## :material/arrow_forward: Next steps for your team")
st.markdown(
    """
1. **Share skills across the team** — Put `$profile-ac-table` and `$release-check` in a shared
   GitHub repo and point `~/.snowflake/cortex/skills.json` at it for every team member.

2. **Add regression checks to your pipeline** — Run `regression_test.sql` as a step in a
   Snowflake Task before any PROD promotion.

3. **Extend AGENTS.md** — Add domain rules specific to Air Canada's naming conventions,
   forbidden operations on live tables, and required column patterns in GROUP BY.

4. **Build a `$flight-analytics` skill** — Encode your most common analysis patterns
   (OTP rate, load factor, ancillary yield) as a reusable skill that any analyst can invoke.

5. **Schedule DQ monitoring** — Create a Snowflake Task that queries DMF results nightly
   and sends an alert if any check fails.
"""
)

st.markdown("---")

st.markdown("## :material/library_books: Resources")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("**Cortex Code (CoCo)**")
        st.markdown(
            """
- [CoCo Documentation](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)
- [CoCo Desktop](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/index)
- [Skills Reference](https://docs.snowflake.com/en/user-guide/cortex-code/extensibility)
- [Hooks Reference](https://docs.snowflake.com/en/user-guide/cortex-code/hooks)
"""
        )

with col2:
    with st.container(border=True):
        st.markdown("**Data Quality**")
        st.markdown(
            """
- [Data Metric Functions](https://docs.snowflake.com/en/user-guide/data-quality-intro)
- [NULL_COUNT](https://docs.snowflake.com/en/sql-reference/functions/null_count)
- [DUPLICATE_COUNT](https://docs.snowflake.com/en/sql-reference/functions/duplicate_count)
- [DQ Monitoring](https://docs.snowflake.com/en/user-guide/data-quality-working-with-dmf)
"""
        )

with col3:
    with st.container(border=True):
        st.markdown("**Governance**")
        st.markdown(
            """
- [AGENTS.md / Settings](https://docs.snowflake.com/en/user-guide/cortex-code/settings)
- [Object Lineage](https://docs.snowflake.com/en/user-guide/object-dependencies)
- [Snowflake Tasks](https://docs.snowflake.com/en/user-guide/tasks-intro)
"""
        )

st.markdown("---")

st.markdown("## :material/terminal: Quick reference card")
st.code(
    """\
MODES:        /plan  |  /bypass  |  Shift+Tab to cycle
FILES:        @path  |  @path$line-range
TABLES:       #DB.SCHEMA.TABLE
SKILLS:       $skill-name  (e.g. $profile-ac-table, $release-check)
BASH:         !command
COMMANDS:     /help  /status  /skill  /hooks  /agents  /tasks
SESSION:      /fork  /rewind  /compact  /rename
TASK BOARD:   Ctrl+D
CONFIG DIR:   ~/.snowflake/cortex/\
""",
    language="text",
)

st.success("Lab complete. Thanks for joining the Air Canada × CoCo HOL!")
