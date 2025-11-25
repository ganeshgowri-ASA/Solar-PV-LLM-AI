"""
Standards Library Page - Standalone Streamlit page
Browse IEC standards with detailed information.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client

st.set_page_config(page_title="Standards Library - Solar PV AI", page_icon="📚", layout="wide")

st.title("📚 Standards Library")
st.markdown("Browse and explore IEC standards for solar PV systems.")

client = get_client()

# Mock standards data for browsing
STANDARDS_DATA = [
    {
        "id": "iec-61215",
        "title": "IEC 61215 - Crystalline Silicon Terrestrial PV Modules",
        "description": "Design qualification and type approval for crystalline silicon terrestrial photovoltaic modules.",
        "category": "Module Testing",
        "difficulty": "Intermediate",
        "sections": ["Visual Inspection", "Thermal Cycling", "Humidity Freeze", "Damp Heat", "UV Test", "Mechanical Load"],
        "version": "2021",
        "status": "Active"
    },
    {
        "id": "iec-61730",
        "title": "IEC 61730 - PV Module Safety Qualification",
        "description": "Safety requirements for photovoltaic module construction and testing.",
        "category": "Safety",
        "difficulty": "Advanced",
        "sections": ["Electrical Insulation", "Fire Resistance", "Mechanical Integrity", "Ground Continuity"],
        "version": "2023",
        "status": "Active"
    },
    {
        "id": "iec-62446",
        "title": "IEC 62446 - Grid Connected PV Systems",
        "description": "Requirements for documentation, commissioning tests and inspection for grid-connected systems.",
        "category": "Systems",
        "difficulty": "Intermediate",
        "sections": ["System Documentation", "Commissioning", "Inspection Checklist", "Performance Verification"],
        "version": "2020",
        "status": "Active"
    },
    {
        "id": "iec-60904",
        "title": "IEC 60904 - PV Devices Measurements",
        "description": "Measurement principles for terrestrial photovoltaic devices.",
        "category": "Measurements",
        "difficulty": "Beginner",
        "sections": ["Reference Devices", "Spectral Response", "Temperature Coefficients", "I-V Characteristics"],
        "version": "2022",
        "status": "Active"
    },
    {
        "id": "iec-61724",
        "title": "IEC 61724 - PV System Performance Monitoring",
        "description": "Guidelines for measurement, data exchange and analysis of PV system performance.",
        "category": "Performance",
        "difficulty": "Intermediate",
        "sections": ["Data Acquisition", "Performance Ratio", "Energy Yield", "Availability"],
        "version": "2021",
        "status": "Active"
    },
    {
        "id": "iec-61853",
        "title": "IEC 61853 - PV Module Performance Testing",
        "description": "Performance testing and energy rating methods for PV modules.",
        "category": "Performance",
        "difficulty": "Advanced",
        "sections": ["Irradiance Response", "Temperature Response", "Angle of Incidence", "Energy Rating"],
        "version": "2022",
        "status": "Active"
    }
]

# Check if viewing a specific standard
if "selected_library_standard" in st.session_state and st.session_state.selected_library_standard:
    # Detail view
    standard = st.session_state.selected_library_standard

    if st.button("← Back to Library"):
        st.session_state.selected_library_standard = None
        st.rerun()

    st.markdown(f"## {standard['title']}")

    # Metadata
    meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)

    with meta_col1:
        st.metric("Category", standard["category"])
    with meta_col2:
        st.metric("Sections", len(standard["sections"]))
    with meta_col3:
        st.metric("Difficulty", standard["difficulty"])
    with meta_col4:
        st.metric("Version", standard["version"])

    st.markdown("---")

    # Description
    st.markdown("### 📝 Description")
    st.info(standard["description"])

    # Version info
    with st.expander("ℹ️ Version Information"):
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.write(f"**Version:** {standard['version']}")
            st.write(f"**Status:** {standard['status']}")
        with v_col2:
            st.write(f"**Standard ID:** {standard['id']}")
            st.write(f"**Category:** {standard['category']}")

    st.markdown("---")

    # Sections
    st.markdown("### 📑 Sections & Content")

    section_tabs = st.tabs(["Overview", "Detailed Sections", "Ask AI"])

    with section_tabs[0]:
        st.markdown(f"This standard contains **{len(standard['sections'])} major sections**.")

        for idx, section in enumerate(standard["sections"], 1):
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                padding: 1rem;
                margin: 0.5rem 0;
                border-left: 4px solid #667eea;
                border-radius: 0.25rem;
            ">
                <strong>{idx}. {section}</strong>
            </div>
            """, unsafe_allow_html=True)

    with section_tabs[1]:
        st.markdown("### Section Details")

        for idx, section in enumerate(standard["sections"], 1):
            with st.expander(f"Section {idx}: {section}"):
                st.markdown(f"""
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
                """)

    with section_tabs[2]:
        st.markdown("### 💬 Ask AI About This Standard")

        question = st.text_input(
            "Your Question",
            placeholder=f"Ask anything about {standard['title']}...",
            key="standard_question"
        )

        if st.button("Ask AI", type="primary"):
            if question:
                with st.spinner("Getting answer..."):
                    try:
                        response = client.chat_query(
                            query=f"Regarding {standard['title']}: {question}"
                        )
                        if response.success:
                            st.markdown("### Answer")
                            st.markdown(response.data.get("answer", "No answer available."))
                        else:
                            st.error(f"Error: {response.error}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        st.markdown("**Suggested Questions:**")
        suggestions = [
            f"What are the key requirements in {standard['title']}?",
            f"What test equipment is needed for {standard['title']}?",
            "What are the acceptance criteria?",
            "How does this differ from related standards?"
        ]

        sug_cols = st.columns(2)
        for idx, sug in enumerate(suggestions):
            with sug_cols[idx % 2]:
                if st.button(sug, key=f"sug_{idx}", use_container_width=True):
                    st.session_state.standard_question = sug
                    st.rerun()

    # Action buttons
    st.markdown("---")
    act_col1, act_col2, act_col3 = st.columns(3)

    with act_col1:
        summary = f"""
{standard['title']}
{'='*60}

METADATA:
- Category: {standard['category']}
- Difficulty: {standard['difficulty']}
- Version: {standard['version']}
- Status: {standard['status']}

DESCRIPTION:
{standard['description']}

SECTIONS ({len(standard['sections'])}):
"""
        for idx, section in enumerate(standard["sections"], 1):
            summary += f"{idx}. {section}\n"

        st.download_button(
            "📥 Download Summary",
            summary,
            f"{standard['id']}_summary.txt",
            "text/plain",
            use_container_width=True
        )

    with act_col2:
        if st.button("🔍 Search Related", use_container_width=True):
            st.info(f"Search for standards related to {standard['category']}")

    with act_col3:
        if st.button("💬 Discuss in Chat", use_container_width=True):
            st.info("Navigate to Chat page for discussion")

else:
    # Library browse view
    st.markdown("### 📂 Browse by Category")

    categories = list(set([std["category"] for std in STANDARDS_DATA]))
    categories.sort()

    selected_category = st.selectbox(
        "Select Category",
        ["All Categories"] + categories,
        index=0
    )

    # Filter standards
    if selected_category != "All Categories":
        displayed_standards = [s for s in STANDARDS_DATA if s["category"] == selected_category]
    else:
        displayed_standards = STANDARDS_DATA

    st.markdown("---")
    st.markdown(f"### 📋 Standards ({len(displayed_standards)})")

    for standard in displayed_standards:
        with st.container():
            s_col1, s_col2 = st.columns([4, 1])

            with s_col1:
                st.markdown(f"#### {standard['title']}")
                st.markdown(standard["description"])

                tag_col1, tag_col2, tag_col3 = st.columns(3)
                with tag_col1:
                    st.caption(f"📁 {standard['category']}")
                with tag_col2:
                    st.caption(f"📊 {len(standard['sections'])} sections")
                with tag_col3:
                    st.caption(f"🎯 {standard['difficulty']}")

            with s_col2:
                if st.button("View Details →", key=f"view_{standard['id']}", use_container_width=True):
                    st.session_state.selected_library_standard = standard
                    st.rerun()

            st.markdown("---")

    # Quick reference
    st.markdown("### ⚡ Quick Reference")

    ref_col1, ref_col2 = st.columns(2)

    with ref_col1:
        st.markdown("""
        **Most Common Standards:**
        1. IEC 61215 - Module Design Qualification
        2. IEC 61730 - Module Safety
        3. IEC 62446 - Grid Connection
        4. IEC 60904 - Measurements
        """)

    with ref_col2:
        st.markdown("""
        **By Testing Phase:**
        - Design: IEC 61215, IEC 61853
        - Safety: IEC 61730, IEC 62109
        - Installation: IEC 62446
        - Monitoring: IEC 61724
        """)
