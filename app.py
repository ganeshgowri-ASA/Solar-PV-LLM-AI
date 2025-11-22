"""
Solar PV LLM AI System - Main Streamlit Application
Interactive frontend for solar PV technical assistance with RAG-powered AI
"""
import streamlit as st
from streamlit_option_menu import option_menu
import sys
from pathlib import Path

# Add project paths
sys.path.append(str(Path(__file__).parent))

from config.settings import (
    APP_NAME,
    APP_VERSION,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
)
from frontend.utils.styles import get_custom_css

# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} v{APP_VERSION}",
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
    menu_items={
        "Get Help": "https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI",
        "Report a bug": "https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues",
        "About": f"{APP_NAME} v{APP_VERSION} - AI-powered Solar PV Technical Assistant",
    },
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Chat"

    if "search_results" not in st.session_state:
        st.session_state.search_results = []

    if "selected_standard" not in st.session_state:
        st.session_state.selected_standard = None

    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None

    if "calculator_results" not in st.session_state:
        st.session_state.calculator_results = {}


def create_sidebar():
    """Create sidebar navigation"""
    with st.sidebar:
        st.image(
            "https://via.placeholder.com/200x80/667eea/ffffff?text=Solar+PV+AI",
            use_container_width=True,
        )

        st.markdown(f"### {APP_NAME}")
        st.caption(f"Version {APP_VERSION}")
        st.divider()

        # Navigation menu
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "Chat",
                "Search",
                "Calculators",
                "Image Analysis",
                "Standards Library",
                "Dashboard",
            ],
            icons=[
                "chat-dots",
                "search",
                "calculator",
                "image",
                "book",
                "speedometer2",
            ],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "#667eea", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "10px",
                },
                "nav-link-selected": {"background-color": "#667eea"},
            },
        )

        st.divider()

        # Quick stats
        st.markdown("### Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", "1,247", "+12%")
        with col2:
            st.metric("Accuracy", "94.3%", "+2.1%")

        st.divider()

        # Help section
        with st.expander("ℹ️ Help & Support"):
            st.markdown("""
            **Getting Started:**
            - Use **Chat** for AI-powered Q&A
            - **Search** IEC standards database
            - Run **Calculators** for system design
            - Upload images for **Analysis**
            - Browse **Standards Library**
            - View **Dashboard** analytics

            **Need Help?**
            Contact support or check documentation.
            """)

        # Footer
        st.markdown("---")
        st.caption("© 2024 Solar PV AI System")

        return selected


def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()

    # Create sidebar and get selected page
    selected_page = create_sidebar()
    st.session_state.selected_page = selected_page

    # Route to selected page
    if selected_page == "Chat":
        from frontend.pages import chat_page
        chat_page.render()

    elif selected_page == "Search":
        from frontend.pages import search_page
        search_page.render()

    elif selected_page == "Calculators":
        from frontend.pages import calculators_page
        calculators_page.render()

    elif selected_page == "Image Analysis":
        from frontend.pages import image_analysis_page
        image_analysis_page.render()

    elif selected_page == "Standards Library":
        from frontend.pages import standards_library_page
        standards_library_page.render()

    elif selected_page == "Dashboard":
        from frontend.pages import dashboard_page
        dashboard_page.render()


if __name__ == "__main__":
    main()
