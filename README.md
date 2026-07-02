# Air Canada × CoCo Hands-On Lab

A 90-minute Cortex Code HOL for Air Canada's data team, focused on:

- Data discovery and analytics enablement
- Data quality rule generation
- Non-regression testing (UAT/PROD)
- Release confidence and validation
- Change impact analysis

## Repository Structure

```
ac-coco-hol/
├── streamlit_app.py          # HOL guide app (deploy to Streamlit Community)
├── setup.sql                 # Creates AC_HOL_DB with synthetic data
├── requirements.txt          # streamlit>=1.30.0
├── .streamlit/
│   └── config.toml           # Air Canada red theme (#E20808)
└── README.md
```

## Step 1 — Run setup.sql

Prerequisites: [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/installation/installation) installed and a connection configured.

```bash
# Run the setup script (creates AC_HOL_DB + synthetic data, ~2-3 min)
snow sql -f setup.sql -c <your-connection-name>
```

**What gets created:**

| Table | Rows | Intentional DQ Issues |
|-------|------|----------------------|
| `AC_HOL_DB.OPERATIONS.FLIGHTS` | ~10,050 | ~200 NULL `delay_reason` on DELAYED flights; ~50 duplicate `flight_id` |
| `AC_HOL_DB.BOOKINGS.RESERVATIONS` | ~25,000 | ~100 NULL `cabin_class` |
| `AC_HOL_DB.LOYALTY.AEROPLAN_MEMBERS` | ~5,000 | ~30 rows with negative `points_balance` |
| `AC_HOL_UAT.FLIGHTS` | ~9,500 | Missing 2 columns (`aircraft_type`, `delay_reason`); 500 fewer rows |
| `AC_HOL_DB.OPERATIONS.FLIGHT_ROUTES` | 20 | Reference/lookup data — clean |

## Step 2 — Run the app locally

```bash
pip install streamlit
streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser.

## Step 3 — Deploy to Streamlit Community Cloud

1. Push this repository to GitHub (public or private)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Connect your GitHub account and select this repository
4. Set **Main file path** to `streamlit_app.py`
5. Click **Deploy** — no secrets required (the app is static content)
6. Share the generated URL with attendees

> The HOL guide app does **not** connect to Snowflake. It is a static interactive guide.
> Attendees connect CoCo directly to their own Snowflake account using `setup.sql`.

## Swap in Real Air Canada Table Names

If attendees have access to real Air Canada tables, replace the synthetic table references
in each section's CoCo prompts. The skill and hook patterns are schema-agnostic.

Example substitution:
```
# Synthetic (lab)
AC_HOL_DB.OPERATIONS.FLIGHTS

# Real (swap in if available)
AIR_CANADA_PROD.OPS.FLIGHT_MASTER
```

## Attendee Prerequisites

- CoCo Desktop installed ([download](https://www.snowflake.com/en/product/limited-access/cortex-code/)) or CoCo CLI (`brew install cortex`)
- Active Snowflake account with ACCOUNTADMIN or equivalent role (to run setup.sql)
- `snow` CLI configured with a connection (`snow connection add`)

## CoCo Quick Reference

| Syntax | Action |
|--------|--------|
| `#DB.SCHEMA.TABLE` | Reference a table directly |
| `$skill-name` | Invoke a skill |
| `@path/to/file` | Reference a file |
| `!command` | Run bash inline |
| `/status` | Show current connection |
| `/plan` | Read-only planning mode |
| `/bypass` | Auto-approve all actions |
| `Ctrl+D` | Open task board |

## Resources

- [CoCo Documentation](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)
- [Data Metric Functions](https://docs.snowflake.com/en/user-guide/data-quality-intro)
- [CoCo Skills](https://docs.snowflake.com/en/user-guide/cortex-code/extensibility)
- [CoCo Hooks](https://docs.snowflake.com/en/user-guide/cortex-code/hooks)
