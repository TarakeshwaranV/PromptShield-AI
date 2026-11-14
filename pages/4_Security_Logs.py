import streamlit as st
import pandas as pd
from core.ui_components import inject_cyber_theme, render_sidebar_header
from core.database import get_security_logs, clear_security_logs

st.set_page_config(
    page_title="Security Logs — PromptShield AI",
    page_icon="📜",
    layout="wide"
)

inject_cyber_theme()
render_sidebar_header()

st.title("📜 Security Audit Logs")
st.caption("Persistent SQLite Security Event Ledger for Forensic & Incident Tracking")

# Summary cards from database
raw_df = get_security_logs(limit=1000)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
total_events = len(raw_df)
blocks = len(raw_df[raw_df["detector_decision"] == "BLOCK"]) if total_events > 0 else 0
tool_rejections = len(raw_df[raw_df["authorization_outcome"].str.startswith("REJECTED", na=False)]) if total_events > 0 else 0
avg_lat = raw_df["execution_latency_ms"].mean() if total_events > 0 else 0.0

col_m1.metric("Total Logged Events", total_events)
col_m2.metric("Layer 1 Perimeter Blocks", blocks)
col_m3.metric("Layer 3 Tool Rejections", tool_rejections)
col_m4.metric("Avg Event Latency", f"{avg_lat:.2f} ms")

st.markdown("---")

# Filter Section
st.markdown("### 🔍 Audit Filters")
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
    cfg_opts = ["All"] + sorted(list(raw_df["chatbot_config"].dropna().unique())) if total_events > 0 else ["All"]
    filter_cfg = st.selectbox("Chatbot Configuration", options=cfg_opts)

with f_col2:
    evt_opts = ["All"] + sorted(list(raw_df["event_type"].dropna().unique())) if total_events > 0 else ["All"]
    filter_evt = st.selectbox("Event Type", options=evt_opts)

with f_col3:
    outcomes = ["All", "BLOCK", "ALLOW", "REVIEW", "AUTHORIZED", "REJECTED_UNAUTHORIZED_TOOL", "REJECTED_ARGUMENT_VIOLATION"]
    filter_outcome = st.selectbox("Security Outcome", options=outcomes)

with f_col4:
    limit_val = st.slider("Max Rows to Display", min_value=25, max_value=500, value=100, step=25)

# Fetch filtered logs
filtered_logs = get_security_logs(
    limit=limit_val,
    chatbot_config=filter_cfg,
    event_type=filter_evt,
    outcome=filter_outcome
)

st.markdown("---")

# Actions: CSV Export and Clear Logs
act_col1, act_col2, _ = st.columns([1.5, 1.5, 4])
with act_col1:
    if not filtered_logs.empty:
        csv_data = filtered_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Logs (CSV)",
            data=csv_data,
            file_name="promptshield_security_logs.csv",
            mime="text/csv",
            use_container_width=True
        )
with act_col2:
    if st.button("🗑️ Clear All Security Logs", use_container_width=True):
        clear_security_logs()
        st.success("Security audit logs table cleared.")
        st.rerun()

# Table display
if filtered_logs.empty:
    st.info("No security logs match the selected filter criteria. Run interactions in the chatbot or evaluation page to generate audit entries.")
else:
    # Format risk score for display
    display_df = filtered_logs.copy()
    if "risk_score" in display_df.columns:
        display_df["risk_score"] = display_df["risk_score"].apply(lambda v: f"{v:.1%}" if pd.notnull(v) else "-")
    if "execution_latency_ms" in display_df.columns:
        display_df["execution_latency_ms"] = display_df["execution_latency_ms"].apply(lambda v: f"{v:.2f} ms" if pd.notnull(v) else "-")
        
    st.dataframe(display_df, use_container_width=True, height=450)

st.caption("🔒 Privacy Guarantee: Credentials, API keys, and sensitive user secrets are sanitized and redacted prior to audit serialization.")
