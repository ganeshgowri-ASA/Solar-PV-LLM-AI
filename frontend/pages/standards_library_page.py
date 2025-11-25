"""
Standards Library Page
Browse IEC standards with detailed information and AI question capability
"""
import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from backend.api.mock_service import mock_api
from frontend.utils.ui_components import (
    show_loading,
    show_info,
    show_empty_state,
)


def render():
    """Render the standards library page"""
    st.title("📚 Standards Library")
    st.markdown(
        "Browse and explore IEC standards for solar PV systems. "
        "View detailed information and ask AI questions about any standard."
    )

    # Check if a specific standard was selected from search
    if hasattr(st.session_state, "selected_standard") and st.session_state.selected_standard:
        render_standard_detail(st.session_state.selected_standard)
    else:
        render_library_browse()


def render_library_browse():
    """Render the main library browsing interface"""

    # Get all standards
    all_standards = mock_api.search_standards()

    # Category filter
    st.markdown("### 📂 Browse by Category")

    categories = list(set([std["category"] for std in all_standards]))
    categories.sort()

    selected_category = st.selectbox(
        "Select Category",
        ["All Categories"] + categories,
        index=0,
    )

    # Filter standards by category
    if selected_category != "All Categories":
        displayed_standards = [
            std for std in all_standards if std["category"] == selected_category
        ]
    else:
        displayed_standards = all_standards

    st.divider()

    # Display standards as cards
    st.markdown(f"### 📋 Standards ({len(displayed_standards)})")

    for standard in displayed_standards:
        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(
                    f"""
                    <div class="dashboard-card">
                        <h3 style="margin: 0 0 0.5rem 0; color: #333;">
                            {standard['title']}
                        </h3>
                        <p style="color: #666; margin: 0 0 0.75rem 0;">
                            {standard['description']}
                        </p>
                        <div style="display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;">
                            <span class="status-badge status-online">
                                📁 {standard['category']}
                            </span>
                            <span class="status-badge" style="background-color: #e3f2fd; color: #0d47a1;">
                                📊 {standard['test_count']} sections
                            </span>
                            <span class="status-badge" style="background-color: #f3e5f5; color: #4a148c;">
                                🎯 {standard['difficulty']}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                if st.button(
                    "View Details →",
                    key=f"view_std_{standard['id']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_standard = standard["id"]
                    st.rerun()

    # Quick reference section
    st.divider()
    st.markdown("### ⚡ Quick Reference")

    quick_col1, quick_col2 = st.columns(2)

    with quick_col1:
        st.markdown(
            """
            **Most Common Standards:**
            1. IEC 61215 - Module Design Qualification
            2. IEC 61730 - Module Safety
            3. IEC 62446 - Grid Connection
            4. IEC 60904 - Measurements
            """
        )

    with quick_col2:
        st.markdown(
            """
            **By Testing Phase:**
            - Design: IEC 61215, IEC 61853
            - Safety: IEC 61730, IEC 62109
            - Installation: IEC 62446
            - Monitoring: IEC 61724
            """
        )


def render_standard_detail(standard_id: str):
    """Render detailed view of a specific standard"""

    # Back button
    if st.button("← Back to Library"):
        st.session_state.selected_standard = None
        st.rerun()

    # Get standard details
    with show_loading("Loading standard details..."):
        standard = mock_api.get_standard_detail(standard_id)

    if not standard:
        st.error("Standard not found.")
        return

    # Header
    st.markdown(f"## {standard['title']}")

    # Metadata
    meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)

    with meta_col1:
        st.metric("Category", standard["category"])

    with meta_col2:
        st.metric("Sections", standard["test_count"])

    with meta_col3:
        st.metric("Difficulty", standard["difficulty"])

    with meta_col4:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div class="status-badge status-online">
                    ✅ {standard['status']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Description
    st.markdown("### 📝 Description")
    st.info(standard["description"])

    # Version information
    with st.expander("ℹ️ Version Information"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Version:** {standard['version']}")
            st.write(f"**Status:** {standard['status']}")
        with col2:
            st.write(f"**Last Updated:** {standard['last_updated']}")
            st.write(f"**Standard ID:** {standard['id']}")

    st.divider()

    # Sections/Content
    st.markdown("### 📑 Sections & Content")

    # Create tabs for different views
    section_tabs = st.tabs(["Overview", "Detailed Sections", "Related Standards"])

    with section_tabs[0]:
        # Overview tab
        st.markdown(
            f"This standard contains **{standard['test_count']} major sections** "
            f"covering various aspects of {standard['category'].lower()}."
        )

        # Display sections as a numbered list
        for idx, section in enumerate(standard["sections"], 1):
            st.markdown(
                f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    border-left: 4px solid #667eea;
                    border-radius: 0.25rem;
                ">
                    <strong>{idx}. {section}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with section_tabs[1]:
        # Detailed sections tab
        st.markdown("### Section Details")

        for idx, section in enumerate(standard["sections"], 1):
            with st.expander(f"Section {idx}: {section}", expanded=False):
                st.markdown(
                    f"""
                    **Section {idx}: {section}**

                    This section covers the requirements and test procedures for {section.lower()}.

                    **Key Points:**
                    - Test methodology and setup
                    - Acceptance criteria
                    - Required equipment and conditions
                    - Reporting requirements

                    **Applicable to:**
                    - Module manufacturers
                    - Testing laboratories
                    - Certification bodies
                    - Quality assurance teams
                    """
                )

                if st.button(
                    f"💬 Ask AI about this section",
                    key=f"ask_section_{idx}",
                ):
                    st.session_state.selected_page = "Chat"
                    st.session_state.chat_history.append(
                        {
                            "role": "user",
                            "content": f"Tell me about {section} in {standard['title']}",
                        }
                    )
                    st.rerun()

    with section_tabs[2]:
        # Related standards tab
        st.markdown("### 🔗 Related Standards")

        if standard.get("related_standards"):
            st.info(
                "These standards are commonly used together or provide complementary information."
            )

            for related_id in standard["related_standards"]:
                related = mock_api.get_standard_detail(related_id)
                if related:
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.markdown(f"**{related['title']}**")
                        st.caption(related["description"])

                    with col2:
                        if st.button("View", key=f"related_{related_id}"):
                            st.session_state.selected_standard = related_id
                            st.rerun()

                    st.divider()
        else:
            show_info("No related standards available.")

    # AI Question Section
    st.divider()
    st.markdown("### 💬 Ask AI About This Standard")

    question_col1, question_col2 = st.columns([3, 1])

    with question_col1:
        user_question = st.text_input(
            "Question",
            placeholder=f"Ask anything about {standard['title']}...",
            label_visibility="collapsed",
            key="standard_question",
        )

    with question_col2:
        ask_button = st.button("Ask AI", type="primary", use_container_width=True)

    if ask_button and user_question:
        # Navigate to chat with pre-filled question
        st.session_state.selected_page = "Chat"

        # Add context about the standard to the question
        contextualized_question = (
            f"Regarding {standard['title']}: {user_question}"
        )

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": contextualized_question,
            }
        )
        st.rerun()

    # Suggested questions
    st.markdown("**Suggested Questions:**")

    suggested_col1, suggested_col2 = st.columns(2)

    suggestions = [
        f"What are the key requirements in {standard['title']}?",
        f"What test equipment is needed for {standard['title']}?",
        f"What are the acceptance criteria in this standard?",
        f"How does {standard['title']} differ from related standards?",
    ]

    for idx, suggestion in enumerate(suggestions):
        col = suggested_col1 if idx % 2 == 0 else suggested_col2
        with col:
            if st.button(
                suggestion,
                key=f"suggestion_{idx}",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.selected_page = "Chat"
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": suggestion,
                    }
                )
                st.rerun()

    # Action buttons
    st.divider()
    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("📥 Download Summary", use_container_width=True):
            summary = f"""
{standard['title']}
{'='*80}

METADATA:
- Category: {standard['category']}
- Difficulty: {standard['difficulty']}
- Version: {standard['version']}
- Status: {standard['status']}
- Last Updated: {standard['last_updated']}

DESCRIPTION:
{standard['description']}

SECTIONS ({standard['test_count']}):
"""
            for idx, section in enumerate(standard["sections"], 1):
                summary += f"{idx}. {section}\n"

            st.download_button(
                "Download",
                summary,
                f"{standard['id']}_summary.txt",
                "text/plain",
                use_container_width=True,
            )

    with action_col2:
        if st.button("🔍 Search Related", use_container_width=True):
            st.session_state.selected_page = "Search"
            st.session_state.search_results = mock_api.search_standards(
                query=standard["category"]
            )
            st.session_state.selected_standard = None
            st.rerun()

    with action_col3:
        if st.button("💬 Discuss in Chat", use_container_width=True):
            st.session_state.selected_page = "Chat"
            st.session_state.selected_standard = None
            st.rerun()
