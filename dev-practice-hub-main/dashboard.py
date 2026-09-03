import pandas as pd
import plotly.express as px
import streamlit as st

from database.services import DatabaseService

st.set_page_config(page_title="AI Job Tracker", page_icon="💼", layout="wide")

db = DatabaseService()
applications = [dict(row) for row in db.get_all()]


def status_of(app):
    """Safely lowercase a status that might be None."""
    return (app.get("status") or "unknown").lower()


# ---------- Stats ----------

total = len(applications)
interview = sum(1 for a in applications if status_of(a) == "interview")
rejected = sum(1 for a in applications if status_of(a) == "rejected")
offer = sum(1 for a in applications if status_of(a) == "offer")
pending = total - interview - rejected - offer

# ---------- Title ----------

st.title("💼 AI Job Tracker Dashboard")

# ---------- Metrics ----------

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Applications", total)
col2.metric("Interviews", interview)
col3.metric("Offers", offer)
col4.metric("Rejected", rejected)
col5.metric("Pending", pending)

st.divider()

# ---------- Filter & Search ----------

status_filter = st.selectbox(
    "Filter by Status", ["All", "Interview", "Offer", "Rejected", "Pending"]
)
search = st.text_input("Search Company")

st.divider()

# ---------- List ----------

for app in applications:
    if status_filter != "All" and status_of(app) != status_filter.lower():
        continue

    if search and search.lower() not in (app.get("company") or "").lower():
        continue

    with st.container():
        st.subheader(app.get("company") or "Unknown")

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Role:** {app.get('role', 'Unknown')}")
            st.write(f"**Status:** {app.get('status', 'Unknown')}")
        with c2:
            st.write(f"**Sender:** {app.get('sender', '')}")
            st.write(f"**Received:** {app.get('received_date', '')}")

        st.write(f"**Subject:** {app.get('subject', '')}")
        st.divider()

# ---------- Analytics ----------
# Previously `df` was only created inside `if applications:` but was
# then used unconditionally further down — a guaranteed NameError on
# an empty database. Both charts now live inside the same guarded block.

st.header("📊 Job Application Analytics")

if applications:
    df = pd.DataFrame(applications)

    status_count = df["status"].fillna("Unknown").value_counts().reset_index()
    status_count.columns = ["Status", "Count"]

    fig = px.pie(
        status_count, names="Status", values="Count",
        title="Application Status Distribution",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.header("🏢 Applications by Company")

    company_count = df["company"].fillna("Unknown").value_counts().reset_index()
    company_count.columns = ["Company", "Applications"]

    fig2 = px.bar(
        company_count, x="Company", y="Applications",
        title="Applications per Company",
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No applications tracked yet. Run `python main.py` to fetch and classify emails.")
