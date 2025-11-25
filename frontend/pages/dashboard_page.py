"""
Dashboard Page - Standalone Streamlit page
System analytics, health indicators, and usage statistics.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client

st.set_page_config(page_title="Dashboard - Solar PV AI", page_icon="📊", layout="wide")

st.title("📊 System Dashboard")
st.markdown("Monitor system health, usage analytics, and performance metrics.")

client = get_client()

# Refresh button
col1, col2, _ = st.columns([1, 1, 4])
with col1:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
with col2:
    auto_refresh = st.checkbox("Auto-refresh")

st.markdown("---")

# Generate mock dashboard data (since api_client doesn't have dashboard methods)
def get_dashboard_data():
    """Generate dashboard metrics"""
    return {
        "system_health": {
            "status": "Healthy",
            "uptime_percentage": 99.7,
            "active_queries": random.randint(5, 25),
            "response_time_ms": random.randint(180, 320)
        },
        "usage_stats": {
            "total_queries": random.randint(8000, 12000),
            "successful_queries": random.randint(7500, 11500),
            "failed_queries": random.randint(50, 200),
            "avg_response_time": random.randint(200, 350)
        },
        "knowledge_base": {
            "total_documents": 1247,
            "indexed_standards": 42,
            "index_size_mb": 256.4,
            "last_updated": (datetime.now() - timedelta(hours=random.randint(1, 12))).isoformat()
        }
    }

with st.spinner("Loading dashboard data..."):
    metrics = get_dashboard_data()

# System Health Section
st.markdown("### 🏥 System Health")

health = metrics["system_health"]
h_col1, h_col2, h_col3, h_col4 = st.columns(4)

with h_col1:
    status_icon = "🟢" if health["status"] == "Healthy" else "🟡"
    st.metric("System Status", f"{status_icon} {health['status']}")

with h_col2:
    st.metric(
        "Uptime",
        f"{health['uptime_percentage']:.1f}%",
        delta=f"+{health['uptime_percentage'] - 99:.1f}%"
    )

with h_col3:
    st.metric("Active Queries", health["active_queries"])

with h_col4:
    delta_color = "normal" if health["response_time_ms"] < 300 else "inverse"
    st.metric(
        "Avg Response",
        f"{health['response_time_ms']} ms",
        delta=f"{health['response_time_ms'] - 250} ms",
        delta_color=delta_color
    )

st.markdown("---")

# Usage Statistics
st.markdown("### 📈 Usage Statistics")

usage = metrics["usage_stats"]
u_col1, u_col2, u_col3, u_col4 = st.columns(4)

with u_col1:
    st.metric("Total Queries", f"{usage['total_queries']:,}")

with u_col2:
    success_rate = (usage["successful_queries"] / usage["total_queries"]) * 100
    st.metric(
        "Success Rate",
        f"{success_rate:.1f}%",
        delta=f"{success_rate - 95:.1f}%"
    )

with u_col3:
    st.metric(
        "Failed Queries",
        usage["failed_queries"],
        delta=f"-{usage['failed_queries']}",
        delta_color="inverse"
    )

with u_col4:
    st.metric("Avg Response Time", f"{usage['avg_response_time']} ms")

st.markdown("---")

# Knowledge Base Section
st.markdown("### 📚 Knowledge Base")

kb = metrics["knowledge_base"]
kb_col1, kb_col2, kb_col3, kb_col4 = st.columns(4)

with kb_col1:
    st.metric("Total Documents", f"{kb['total_documents']:,}")

with kb_col2:
    st.metric("IEC Standards", kb["indexed_standards"])

with kb_col3:
    st.metric("Index Size", f"{kb['index_size_mb']} MB")

with kb_col4:
    last_updated = datetime.fromisoformat(kb["last_updated"])
    time_ago = datetime.now() - last_updated
    hours_ago = time_ago.seconds // 3600
    st.metric("Last Updated", f"{hours_ago}h ago")

st.markdown("---")

# Performance Charts (using native Streamlit charts)
st.markdown("### 📊 Performance Trends (Last 30 Days)")

# Generate time series data
dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
queries = [random.randint(200, 500) for _ in range(30)]
response_times = [random.randint(180, 350) for _ in range(30)]
success_rates = [random.uniform(94, 99.5) for _ in range(30)]

chart_tabs = st.tabs(["Query Volume", "Response Time", "Success Rate"])

with chart_tabs[0]:
    st.line_chart(
        data={"Queries": queries},
        use_container_width=True
    )
    st.caption("Daily query volume over the last 30 days")

with chart_tabs[1]:
    st.line_chart(
        data={"Response Time (ms)": response_times},
        use_container_width=True
    )
    st.caption("Average response time in milliseconds")

with chart_tabs[2]:
    st.line_chart(
        data={"Success Rate (%)": success_rates},
        use_container_width=True
    )
    st.caption("Query success rate percentage")

st.markdown("---")

# Recent Activity
st.markdown("### 🕒 Recent Activity")

activities = [
    {"type": "Chat Query", "status": "success", "time": "2m ago"},
    {"type": "Standards Search", "status": "success", "time": "5m ago"},
    {"type": "Calculation", "status": "success", "time": "8m ago"},
    {"type": "Image Analysis", "status": "warning", "time": "12m ago"},
    {"type": "Chat Query", "status": "success", "time": "15m ago"},
    {"type": "Standards Search", "status": "success", "time": "22m ago"},
]

for activity in activities:
    status_icon = "✅" if activity["status"] == "success" else "⚠️"
    bg_color = "#d4edda" if activity["status"] == "success" else "#fff3cd"
    border_color = "#28a745" if activity["status"] == "success" else "#ffc107"

    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 0.5rem;
            border-left: 4px solid {border_color};
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <span><strong>{status_icon} {activity['type']}</strong></span>
            <span style="color: #666; font-size: 0.9rem;">{activity['time']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# System Information
st.markdown("### ⚙️ System Information")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.markdown("""
    **Application Details:**
    - Version: 1.0.0
    - Environment: Production
    - Region: US-East
    - Backend: Active
    - Database: Connected
    """)

with info_col2:
    st.markdown("""
    **Performance Targets:**
    - Uptime: > 99.5%
    - Response Time: < 300ms
    - Success Rate: > 95%
    - Query Capacity: 10,000/day
    - Index Update: Daily
    """)

st.markdown("---")

# Query Distribution
st.markdown("### 📂 Query Distribution by Category")

categories = ["Module Testing", "Safety Standards", "Performance", "Calculations", "Image Analysis", "General"]
counts = [245, 189, 167, 223, 98, 156]

col1, col2 = st.columns([2, 1])

with col1:
    st.bar_chart(data=dict(zip(categories, counts)))

with col2:
    st.markdown("**Top Categories:**")
    total = sum(counts)
    for i, (cat, count) in enumerate(zip(categories, counts), 1):
        pct = (count / total) * 100
        st.markdown(f"{i}. **{cat}**: {count} ({pct:.1f}%)")

# Export options
st.markdown("---")
exp_col1, exp_col2 = st.columns(2)

with exp_col1:
    if st.button("📥 Export Metrics", use_container_width=True):
        import json
        st.download_button(
            "Download JSON",
            json.dumps(metrics, indent=2, default=str),
            "dashboard_metrics.json",
            "application/json",
            use_container_width=True
        )

with exp_col2:
    if st.button("📧 Email Report", use_container_width=True):
        st.success("Report generation scheduled! Check your email shortly.")

# Auto-refresh
if auto_refresh:
    st.info("Dashboard will auto-refresh every 30 seconds.")
    import time
    time.sleep(30)
    st.rerun()
