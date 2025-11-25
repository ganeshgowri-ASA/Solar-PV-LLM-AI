"""
Solar PV LLM AI - Streamlit Frontend
Main application with real API integration.
"""

import sys
import os
from pathlib import Path

# Add both project root and frontend directory to Python path for Streamlit Cloud
project_root = Path(__file__).parent.parent
frontend_dir = Path(__file__).parent

# Add paths for imports - frontend dir first for api_client, then project root
for path in [str(frontend_dir), str(project_root)]:
    if path not in sys.path:
        sys.path.insert(0, path)

import streamlit as st
import time
from typing import Optional

# Import API client with error handling
try:
    from api_client import (
        get_client,
        SolarPVAPIClient,
        ExpertiseLevel,
        CalculationType,
        APIResponse
    )
except ImportError as e:
    st.error(f"Failed to import API client: {e}. Please ensure api_client.py is in the frontend directory.")
    st.stop()


# ============ Page Configuration ============

st.set_page_config(
    page_title="Solar PV AI Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============ Custom CSS ============

st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }

    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }

    /* Citation styling */
    .citation-box {
        background-color: #f0f7ff;
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 5px 5px 0;
    }

    /* Status indicators */
    .status-healthy {
        color: #4CAF50;
        font-weight: bold;
    }

    .status-error {
        color: #f44336;
        font-weight: bold;
    }

    /* Chat message styling */
    .user-message {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }

    .assistant-message {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }

    /* Results card */
    .result-card {
        background-color: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ============ Session State Initialization ============

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "api_client": None,
        "chat_history": [],
        "conversation_id": None,
        "expertise_level": ExpertiseLevel.INTERMEDIATE,
        "backend_status": None,
        "last_health_check": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_api_client() -> SolarPVAPIClient:
    """Get or create API client."""
    try:
        if st.session_state.get("api_client") is None:
            st.session_state.api_client = get_client()
        return st.session_state.api_client
    except Exception as e:
        st.error(f"Failed to initialize API client: {e}")
        return get_client()  # Return a new client as fallback


def check_backend_status() -> bool:
    """Check backend status (cached for 30 seconds)."""
    try:
        current_time = time.time()

        # Check every 30 seconds
        if current_time - st.session_state.get("last_health_check", 0) > 30:
            try:
                client = get_api_client()
                st.session_state.backend_status = client.is_healthy()
            except Exception:
                st.session_state.backend_status = False
            st.session_state.last_health_check = current_time

        return st.session_state.get("backend_status", False)
    except Exception:
        return False


# ============ Sidebar ============

def render_sidebar():
    """Render sidebar with navigation and settings."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/solar-panel.png", width=80)
        st.title("Solar PV AI")

        # Backend status
        st.subheader("System Status")
        status = check_backend_status()

        if status:
            st.success("Backend: Connected")
        else:
            st.error("Backend: Disconnected")
            st.caption("Make sure the backend is running on localhost:8000")

        st.divider()

        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Select Page",
            ["Chat Assistant", "Standards Search", "Calculator", "Image Analysis"],
            label_visibility="collapsed"
        )

        st.divider()

        # Settings
        st.subheader("Settings")
        expertise = st.selectbox(
            "Expertise Level",
            options=[e.value for e in ExpertiseLevel],
            index=1,
            help="Adjust response complexity"
        )
        st.session_state.expertise_level = ExpertiseLevel(expertise)

        st.divider()

        # Info
        st.caption("Solar PV AI Assistant v1.0")
        st.caption("Powered by RAG + LLM")

        return page


# ============ Chat Page ============

def render_chat_page():
    """Render the chat assistant page."""
    st.markdown('<p class="main-header">Chat with Solar PV AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask any question about solar PV systems, installation, standards, or calculations.</p>', unsafe_allow_html=True)

    client = get_api_client()

    # Chat container
    chat_container = st.container()

    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])

                    # Show citations if available
                    if message.get("citations"):
                        with st.expander("View Citations"):
                            for citation in message["citations"]:
                                st.markdown(f"""
                                <div class="citation-box">
                                    <strong>{citation.get('source', 'Unknown')}</strong>
                                    {f" - Section {citation.get('section')}" if citation.get('section') else ""}
                                    <br><em>"{citation.get('text', '')}"</em>
                                    <br><small>Relevance: {citation.get('relevance_score', 0):.0%}</small>
                                </div>
                                """, unsafe_allow_html=True)

                    # Show follow-up questions
                    if message.get("follow_ups"):
                        st.caption("Suggested follow-up questions:")
                        cols = st.columns(len(message["follow_ups"]))
                        for i, question in enumerate(message["follow_ups"]):
                            with cols[i]:
                                if st.button(question, key=f"followup_{len(st.session_state.chat_history)}_{i}"):
                                    st.session_state.pending_question = question
                                    st.rerun()

    # Handle pending question from follow-up buttons
    if "pending_question" in st.session_state:
        pending = st.session_state.pending_question
        del st.session_state.pending_question
        process_chat_query(client, pending)
        st.rerun()

    # Chat input
    query = st.chat_input("Ask about solar PV systems...")

    if query:
        process_chat_query(client, query)
        st.rerun()

    # Streaming toggle
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        stream_enabled = st.checkbox("Enable streaming", value=False, help="Stream responses in real-time")
        st.session_state.stream_enabled = stream_enabled

    # Clear chat button
    with col1:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.conversation_id = None
            st.rerun()


def process_chat_query(client: SolarPVAPIClient, query: str):
    """Process a chat query and update history."""
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })

    # Check if streaming is enabled
    if st.session_state.get("stream_enabled", False):
        # Stream response
        full_response = ""
        for token in client.chat_stream(
            query=query,
            expertise_level=st.session_state.expertise_level,
            conversation_id=st.session_state.conversation_id
        ):
            full_response += token

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_response,
            "citations": [],
            "follow_ups": []
        })
    else:
        # Regular request
        response = client.chat_query(
            query=query,
            expertise_level=st.session_state.expertise_level,
            conversation_id=st.session_state.conversation_id,
            include_citations=True
        )

        if response.success:
            data = response.data
            st.session_state.conversation_id = data.get("conversation_id")

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": data.get("response", "Sorry, I couldn't generate a response."),
                "citations": data.get("citations", []),
                "follow_ups": data.get("follow_up_questions", [])
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Error: {response.error}",
                "citations": [],
                "follow_ups": []
            })


# ============ Search Page ============

def render_search_page():
    """Render the standards search page."""
    st.markdown('<p class="main-header">Solar PV Standards Search</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Search through solar PV standards, codes, and regulations.</p>', unsafe_allow_html=True)

    client = get_api_client()

    # Search controls
    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input(
            "Search Query",
            placeholder="e.g., safety requirements, performance monitoring, installation...",
            label_visibility="collapsed"
        )

    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True)

    # Filters
    with st.expander("Advanced Filters"):
        col1, col2 = st.columns(2)

        with col1:
            # Get categories
            categories_response = client.get_categories()
            if categories_response.success:
                available_categories = categories_response.data
            else:
                available_categories = ["Safety", "Performance", "Installation", "Electrical", "Design"]

            selected_categories = st.multiselect(
                "Filter by Category",
                options=available_categories,
                default=None
            )

        with col2:
            max_results = st.slider("Max Results", 5, 50, 10)
            include_summaries = st.checkbox("Include Summaries", value=True)

    # Perform search
    if search_button and search_query:
        with st.spinner("Searching standards database..."):
            response = client.search_standards(
                query=search_query,
                categories=selected_categories if selected_categories else None,
                max_results=max_results,
                include_summaries=include_summaries
            )

        if response.success:
            results = response.data.get("results", [])
            total_count = response.data.get("total_count", 0)

            st.success(f"Found {total_count} matching standards")

            if results:
                for i, doc in enumerate(results):
                    with st.expander(
                        f"{doc.get('standard_code', 'N/A')} - {doc.get('title', 'Untitled')}",
                        expanded=(i == 0)
                    ):
                        col1, col2, col3 = st.columns([2, 1, 1])

                        with col1:
                            st.markdown(f"**Category:** {doc.get('category', 'N/A')}")
                        with col2:
                            relevance = doc.get('relevance_score', 0)
                            st.markdown(f"**Relevance:** {relevance:.0%}")
                        with col3:
                            st.markdown(f"**ID:** {doc.get('id', 'N/A')}")

                        if include_summaries and doc.get("summary"):
                            st.markdown("---")
                            st.markdown(doc["summary"])

                        if doc.get("sections"):
                            st.markdown("---")
                            st.markdown("**Key Sections:**")
                            for section in doc["sections"]:
                                st.markdown(f"- {section}")
            else:
                st.info("No results found. Try different search terms.")
        else:
            st.error(f"Search failed: {response.error}")

    # Popular searches
    st.markdown("---")
    st.subheader("Popular Searches")

    popular = [
        "Safety requirements",
        "Performance monitoring",
        "Grid interconnection",
        "Inverter standards",
        "Installation guidelines"
    ]

    cols = st.columns(len(popular))
    for i, term in enumerate(popular):
        with cols[i]:
            if st.button(term, key=f"popular_{i}"):
                st.session_state.search_query = term
                st.rerun()


# ============ Calculator Page ============

def render_calculator_page():
    """Render the solar calculator page."""
    st.markdown('<p class="main-header">Solar PV Calculator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Calculate system size, energy output, ROI, and more.</p>', unsafe_allow_html=True)

    client = get_api_client()

    # Calculator type selection
    calc_type = st.selectbox(
        "Select Calculation Type",
        options=[
            ("System Size", CalculationType.SYSTEM_SIZE),
            ("Energy Output", CalculationType.ENERGY_OUTPUT),
            ("Return on Investment (ROI)", CalculationType.ROI),
            ("Payback Period", CalculationType.PAYBACK_PERIOD),
            ("Panel Count", CalculationType.PANEL_COUNT),
            ("Inverter Size", CalculationType.INVERTER_SIZE),
            ("Battery Size", CalculationType.BATTERY_SIZE),
        ],
        format_func=lambda x: x[0]
    )

    selected_calc = calc_type[1]

    st.markdown("---")

    # Dynamic parameter inputs based on calculation type
    parameters = {}

    if selected_calc == CalculationType.SYSTEM_SIZE:
        st.subheader("System Size Calculator")
        col1, col2 = st.columns(2)
        with col1:
            parameters["annual_kwh"] = st.number_input("Annual Energy Usage (kWh)", value=10000, step=500)
            parameters["peak_sun_hours"] = st.slider("Peak Sun Hours", 3.0, 7.0, 5.0, 0.1)
        with col2:
            parameters["performance_ratio"] = st.slider("Performance Ratio", 0.70, 0.90, 0.80, 0.01)
            parameters["panel_wattage"] = st.number_input("Panel Wattage (W)", value=400, step=10)

    elif selected_calc == CalculationType.ENERGY_OUTPUT:
        st.subheader("Energy Output Calculator")
        col1, col2 = st.columns(2)
        with col1:
            parameters["system_size_kw"] = st.number_input("System Size (kW)", value=6.0, step=0.5)
            parameters["peak_sun_hours"] = st.slider("Peak Sun Hours", 3.0, 7.0, 5.0, 0.1)
        with col2:
            parameters["performance_ratio"] = st.slider("Performance Ratio", 0.70, 0.90, 0.80, 0.01)

    elif selected_calc == CalculationType.ROI:
        st.subheader("ROI Calculator")
        col1, col2 = st.columns(2)
        with col1:
            parameters["system_cost"] = st.number_input("System Cost ($)", value=15000, step=500)
            parameters["annual_kwh"] = st.number_input("Annual Production (kWh)", value=8000, step=500)
            parameters["electricity_rate"] = st.number_input("Electricity Rate ($/kWh)", value=0.12, step=0.01, format="%.2f")
        with col2:
            parameters["annual_rate_increase"] = st.slider("Annual Rate Increase (%)", 0.0, 10.0, 3.0, 0.5) / 100
            parameters["incentive_percent"] = st.slider("Incentive/Tax Credit (%)", 0, 50, 30)

    elif selected_calc == CalculationType.PAYBACK_PERIOD:
        st.subheader("Payback Period Calculator")
        col1, col2 = st.columns(2)
        with col1:
            parameters["system_cost"] = st.number_input("System Cost ($)", value=15000, step=500)
            parameters["annual_kwh"] = st.number_input("Annual Production (kWh)", value=8000, step=500)
        with col2:
            parameters["electricity_rate"] = st.number_input("Electricity Rate ($/kWh)", value=0.12, step=0.01, format="%.2f")
            parameters["incentive_percent"] = st.slider("Incentive/Tax Credit (%)", 0, 50, 30)

    elif selected_calc == CalculationType.PANEL_COUNT:
        st.subheader("Panel Count Calculator")
        col1, col2 = st.columns(2)
        with col1:
            parameters["target_kwh_annual"] = st.number_input("Target Annual Production (kWh)", value=10000, step=500)
            parameters["panel_wattage"] = st.number_input("Panel Wattage (W)", value=400, step=10)
        with col2:
            parameters["peak_sun_hours"] = st.slider("Peak Sun Hours", 3.0, 7.0, 5.0, 0.1)
            parameters["efficiency_factor"] = st.slider("Efficiency Factor", 0.70, 0.90, 0.80, 0.01)

    elif selected_calc == CalculationType.INVERTER_SIZE:
        st.subheader("Inverter Size Calculator")
        col1, col2 = st.columns(2)
        with col1:
            parameters["array_size_kw"] = st.number_input("Array Size (kW DC)", value=6.0, step=0.5)
        with col2:
            parameters["dc_ac_ratio"] = st.slider("DC/AC Ratio", 1.0, 1.5, 1.2, 0.05)

    elif selected_calc == CalculationType.BATTERY_SIZE:
        st.subheader("Battery Size Calculator")
        col1, col2 = st.columns(2)
        with col1:
            parameters["daily_kwh"] = st.number_input("Daily Energy Usage (kWh)", value=30, step=5)
            parameters["backup_days"] = st.slider("Backup Days", 0.5, 3.0, 1.0, 0.5)
        with col2:
            parameters["depth_of_discharge"] = st.slider("Depth of Discharge (%)", 50, 95, 80) / 100
            parameters["backup_percentage"] = st.slider("% of Home to Backup", 25, 100, 100, 25)

    # Calculate button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        calculate = st.button("Calculate", type="primary", use_container_width=True)
    with col2:
        include_explanation = st.checkbox("Show Explanation", value=True)

    if calculate:
        with st.spinner("Calculating..."):
            response = client.calculate(
                calculation_type=selected_calc,
                parameters=parameters,
                include_explanation=include_explanation
            )

        if response.success:
            data = response.data

            # Results
            st.subheader("Results")

            result = data.get("result", {})
            cols = st.columns(len(result))

            for i, (key, value) in enumerate(result.items()):
                with cols[i % len(cols)]:
                    display_key = key.replace("_", " ").title()
                    if isinstance(value, float):
                        st.metric(display_key, f"{value:,.2f}")
                    else:
                        st.metric(display_key, f"{value:,}")

            # Explanation
            if include_explanation and data.get("explanation"):
                with st.expander("Calculation Explanation", expanded=True):
                    st.markdown(data["explanation"])

            # Assumptions
            if data.get("assumptions"):
                with st.expander("Assumptions"):
                    for assumption in data["assumptions"]:
                        st.markdown(f"- {assumption}")

            # Recommendations
            if data.get("recommendations"):
                with st.expander("Recommendations"):
                    for rec in data["recommendations"]:
                        st.info(rec)

        else:
            st.error(f"Calculation failed: {response.error}")


# ============ Image Analysis Page ============

def render_image_analysis_page():
    """Render the image analysis page."""
    st.markdown('<p class="main-header">Solar Panel Image Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload images of solar panels for AI-powered analysis.</p>', unsafe_allow_html=True)

    client = get_api_client()

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Solar Panel Image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload a clear image of solar panels for analysis"
    )

    # Analysis options
    col1, col2 = st.columns(2)

    with col1:
        analysis_type = st.selectbox(
            "Analysis Type",
            options=[
                ("General Analysis", "general"),
                ("Defect Detection", "defect_detection"),
                ("Shading Analysis", "shading"),
                ("Layout Analysis", "layout")
            ],
            format_func=lambda x: x[0]
        )

    with col2:
        include_recommendations = st.checkbox("Include Recommendations", value=True)

    if uploaded_file:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Uploaded Image")
            st.image(uploaded_file, use_container_width=True)

        with col2:
            st.subheader("Analysis")

            if st.button("Analyze Image", type="primary", use_container_width=True):
                with st.spinner("Analyzing image..."):
                    # Read image data
                    image_data = uploaded_file.getvalue()

                    response = client.analyze_image(
                        image_data=image_data,
                        analysis_type=analysis_type[1],
                        include_recommendations=include_recommendations
                    )

                if response.success:
                    data = response.data

                    # Confidence score
                    confidence = data.get("confidence_score", 0)
                    st.metric("Analysis Confidence", f"{confidence:.0%}")

                    # Main analysis
                    st.markdown("---")
                    st.markdown(data.get("analysis", "No analysis available."))

                    # Detected elements
                    if data.get("detected_elements"):
                        st.markdown("---")
                        st.subheader("Detected Elements")
                        for element in data["detected_elements"]:
                            element_type = element.get("type", "Unknown")
                            element_conf = element.get("confidence", 0)
                            st.markdown(f"- **{element_type}**: {element_conf:.0%} confidence")

                    # Issues found
                    if data.get("issues_found"):
                        st.markdown("---")
                        st.subheader("Issues Found")
                        for issue in data["issues_found"]:
                            severity = issue.get("severity", "info")
                            if severity == "warning":
                                st.warning(issue.get("description", "Unknown issue"))
                            elif severity == "error":
                                st.error(issue.get("description", "Unknown issue"))
                            else:
                                st.info(issue.get("description", "Unknown issue"))

                    # Recommendations
                    if include_recommendations and data.get("recommendations"):
                        st.markdown("---")
                        st.subheader("Recommendations")
                        for rec in data["recommendations"]:
                            st.success(rec)
                else:
                    st.error(f"Analysis failed: {response.error}")

    # Tips section
    st.markdown("---")
    st.subheader("Tips for Better Analysis")

    tips = [
        "Use high-resolution images for more accurate detection",
        "Include the full solar array in the frame when possible",
        "For defect detection, capture close-up shots of problem areas",
        "Take photos during daylight for best results",
        "Multiple angles can help with comprehensive analysis"
    ]

    for tip in tips:
        st.markdown(f"- {tip}")


# ============ Main Application ============

def main():
    """Main application entry point."""
    try:
        # Initialize session state
        init_session_state()

        # Render sidebar and get selected page
        try:
            page = render_sidebar()
        except Exception as e:
            st.error(f"Error rendering sidebar: {e}")
            page = "Chat Assistant"  # Default page

        # Render selected page
        try:
            if page == "Chat Assistant":
                render_chat_page()
            elif page == "Standards Search":
                render_search_page()
            elif page == "Calculator":
                render_calculator_page()
            elif page == "Image Analysis":
                render_image_analysis_page()
        except Exception as e:
            st.error(f"Error rendering page: {e}")
            st.info("Please try refreshing the page or contact support if the issue persists.")
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please refresh the page to try again.")


if __name__ == "__main__":
    main()
