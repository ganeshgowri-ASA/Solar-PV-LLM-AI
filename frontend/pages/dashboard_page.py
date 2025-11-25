"""
Dashboard Page
System analytics, health indicators, and usage statistics
"""
import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from backend.api.mock_service import mock_api
from frontend.utils.ui_components import show_loading


def render():
    """Render the dashboard page"""
    st.title("📊 System Dashboard")
    st.markdown(
        "Monitor system health, usage analytics, and performance metrics in real-time."
    )

    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=False)

    # Get dashboard data
    with show_loading("Loading dashboard data..."):
        metrics = mock_api.get_dashboard_metrics()
        time_series_data = mock_api.get_time_series_data(days=30)

    st.divider()

    # System Health Section
    st.markdown("### 🏥 System Health")

    health_data = metrics["system_health"]

    health_col1, health_col2, health_col3, health_col4 = st.columns(4)

    with health_col1:
        status_color = "🟢" if health_data["status"] == "Healthy" else "🟡"
        st.metric(
            "System Status",
            f"{status_color} {health_data['status']}",
        )

    with health_col2:
        st.metric(
            "Uptime",
            f"{health_data['uptime_percentage']:.1f}%",
            delta=f"+{health_data['uptime_percentage'] - 99:.1f}%",
            delta_color="normal",
        )

    with health_col3:
        st.metric(
            "Active Queries",
            health_data["active_queries"],
        )

    with health_col4:
        response_color = "normal" if health_data["response_time_ms"] < 300 else "inverse"
        st.metric(
            "Avg Response",
            f"{health_data['response_time_ms']} ms",
            delta=f"{health_data['response_time_ms'] - 250} ms",
            delta_color=response_color,
        )

    st.divider()

    # Usage Statistics
    st.markdown("### 📈 Usage Statistics")

    usage_data = metrics["usage_stats"]

    usage_col1, usage_col2, usage_col3, usage_col4 = st.columns(4)

    with usage_col1:
        st.metric(
            "Total Queries",
            f"{usage_data['total_queries']:,}",
        )

    with usage_col2:
        success_rate = (
            usage_data["successful_queries"] / usage_data["total_queries"] * 100
        )
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            delta=f"{success_rate - 95:.1f}%",
        )

    with usage_col3:
        st.metric(
            "Failed Queries",
            usage_data["failed_queries"],
            delta=f"-{usage_data['failed_queries']}",
            delta_color="inverse",
        )

    with usage_col4:
        st.metric(
            "Avg Response Time",
            f"{usage_data['avg_response_time']} ms",
        )

    st.divider()

    # Knowledge Base Section
    st.markdown("### 📚 Knowledge Base")

    kb_data = metrics["knowledge_base"]

    kb_col1, kb_col2, kb_col3, kb_col4 = st.columns(4)

    with kb_col1:
        st.metric(
            "Total Documents",
            f"{kb_data['total_documents']:,}",
        )

    with kb_col2:
        st.metric(
            "IEC Standards",
            kb_data["indexed_standards"],
        )

    with kb_col3:
        st.metric(
            "Index Size",
            f"{kb_data['index_size_mb']} MB",
        )

    with kb_col4:
        last_updated = datetime.fromisoformat(kb_data["last_updated"])
        time_ago = datetime.now() - last_updated
        st.metric(
            "Last Updated",
            f"{time_ago.seconds // 3600}h ago",
        )

    st.divider()

    # Time Series Charts
    st.markdown("### 📊 Performance Trends (Last 30 Days)")

    chart_tabs = st.tabs(["Query Volume", "Response Time", "Success Rate"])

    with chart_tabs[0]:
        # Query volume chart
        fig_queries = go.Figure()
        fig_queries.add_trace(
            go.Scatter(
                x=time_series_data["date"],
                y=time_series_data["queries"],
                mode="lines+markers",
                fill="tozeroy",
                line=dict(color="#667eea", width=2),
                marker=dict(size=6),
                name="Queries",
            )
        )
        fig_queries.update_layout(
            title="Daily Query Volume",
            xaxis_title="Date",
            yaxis_title="Number of Queries",
            height=400,
            hovermode="x unified",
        )
        st.plotly_chart(fig_queries, use_container_width=True)

    with chart_tabs[1]:
        # Response time chart
        fig_response = go.Figure()
        fig_response.add_trace(
            go.Scatter(
                x=time_series_data["date"],
                y=time_series_data["response_time"],
                mode="lines+markers",
                line=dict(color="#764ba2", width=2),
                marker=dict(size=6),
                name="Response Time",
            )
        )
        fig_response.add_hline(
            y=300,
            line_dash="dash",
            line_color="red",
            annotation_text="Target: 300ms",
        )
        fig_response.update_layout(
            title="Average Response Time",
            xaxis_title="Date",
            yaxis_title="Response Time (ms)",
            height=400,
            hovermode="x unified",
        )
        st.plotly_chart(fig_response, use_container_width=True)

    with chart_tabs[2]:
        # Success rate chart
        fig_success = go.Figure()
        fig_success.add_trace(
            go.Scatter(
                x=time_series_data["date"],
                y=time_series_data["success_rate"],
                mode="lines+markers",
                fill="tozeroy",
                line=dict(color="#28a745", width=2),
                marker=dict(size=6),
                name="Success Rate",
            )
        )
        fig_success.add_hline(
            y=95,
            line_dash="dash",
            line_color="orange",
            annotation_text="Target: 95%",
        )
        fig_success.update_layout(
            title="Query Success Rate",
            xaxis_title="Date",
            yaxis_title="Success Rate (%)",
            height=400,
            hovermode="x unified",
        )
        st.plotly_chart(fig_success, use_container_width=True)

    st.divider()

    # Recent Activity
    st.markdown("### 🕒 Recent Activity")

    activity_data = metrics["recent_activity"]

    # Display recent activity in a table-like format
    for activity in activity_data[:10]:
        timestamp = datetime.fromisoformat(activity["timestamp"])
        time_ago = datetime.now() - timestamp

        if time_ago.seconds < 60:
            time_str = f"{time_ago.seconds}s ago"
        elif time_ago.seconds < 3600:
            time_str = f"{time_ago.seconds // 60}m ago"
        else:
            time_str = f"{time_ago.seconds // 3600}h ago"

        status_icon = (
            "✅" if activity["status"] == "success"
            else "⚠️" if activity["status"] == "warning"
            else "❌"
        )

        st.markdown(
            f"""
            <div style="
                background-color: {'#d4edda' if activity['status'] == 'success' else '#fff3cd'};
                padding: 0.75rem;
                margin: 0.5rem 0;
                border-radius: 0.5rem;
                border-left: 4px solid {'#28a745' if activity['status'] == 'success' else '#ffc107'};
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <span><strong>{status_icon} {activity['type']}</strong></span>
                <span style="color: #666; font-size: 0.9rem;">{time_str}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # System Information
    st.markdown("### ⚙️ System Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown(
            """
            **Application Details:**
            - Version: 1.0.0
            - Environment: Production
            - Region: US-East
            - Backend: Active
            - Database: Connected
            """
        )

    with info_col2:
        st.markdown(
            """
            **Performance Targets:**
            - Uptime: > 99.5%
            - Response Time: < 300ms
            - Success Rate: > 95%
            - Query Capacity: 10,000/day
            - Index Update: Daily
            """
        )

    # Category Distribution
    st.divider()
    st.markdown("### 📂 Query Distribution by Category")

    category_data = {
        "Category": [
            "Module Testing",
            "Safety Standards",
            "Performance Analysis",
            "Calculations",
            "Image Analysis",
            "General Queries",
        ],
        "Count": [245, 189, 167, 223, 98, 156],
    }

    fig_pie = px.pie(
        category_data,
        values="Count",
        names="Category",
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig_pie.update_layout(height=400)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("**Top Categories:**")
        for idx, (cat, count) in enumerate(
            zip(category_data["Category"], category_data["Count"]), 1
        ):
            percentage = (count / sum(category_data["Count"])) * 100
            st.markdown(
                f"{idx}. **{cat}**  \n"
                f"   {count} queries ({percentage:.1f}%)"
            )

    # Export data
    st.divider()

    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        if st.button("📥 Export Metrics", use_container_width=True):
            import json

            export_data = json.dumps(metrics, indent=2)
            st.download_button(
                "Download JSON",
                export_data,
                "dashboard_metrics.json",
                "application/json",
                use_container_width=True,
            )

    with export_col2:
        if st.button("📊 Export Charts", use_container_width=True):
            csv_data = time_series_data.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv_data,
                "time_series_data.csv",
                "text/csv",
                use_container_width=True,
            )

    with export_col3:
        if st.button("📧 Email Report", use_container_width=True):
            st.success("Report generation scheduled! Check your email in a few minutes.")

    # Auto-refresh logic
    if auto_refresh:
        st.info("Dashboard will auto-refresh every 30 seconds.")
        import time

        time.sleep(30)
        st.rerun()
