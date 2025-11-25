"""
Search Page - Standalone Streamlit page
Advanced search for IEC standards and technical documents.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client

st.set_page_config(page_title="Search - Solar PV AI", page_icon="🔍", layout="wide")

st.title("🔍 Advanced Search")
st.markdown("Search through IEC standards, technical documents, and testing procedures.")

client = get_client()

# Search bar
search_col1, search_col2 = st.columns([4, 1])

with search_col1:
    search_query = st.text_input(
        "Search",
        placeholder="Enter keywords: e.g., 'thermal cycling', 'module safety', 'IEC 61215'",
        label_visibility="collapsed"
    )

with search_col2:
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

st.markdown("---")

# Filters
st.markdown("### 🎯 Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    category_filter = st.multiselect(
        "Categories",
        options=["Module Testing", "Safety", "Performance", "Systems", "Measurements"],
        default=[]
    )

with filter_col2:
    difficulty_filter = st.multiselect(
        "Difficulty Level",
        options=["Beginner", "Intermediate", "Advanced"],
        default=[]
    )

with filter_col3:
    sort_by = st.selectbox(
        "Sort By",
        options=["Relevance", "Title (A-Z)", "Title (Z-A)", "Most Recent"],
        index=0
    )

# Additional filters
with st.expander("🔧 More Filters"):
    more_col1, more_col2 = st.columns(2)

    with more_col1:
        standard_types = st.multiselect(
            "Standard Types",
            options=["IEC", "IEEE", "UL", "NFPA", "ASTM"],
            default=[]
        )

    with more_col2:
        max_results = st.slider("Max Results", 5, 50, 20)

st.markdown("---")

# Perform search
if search_button or search_query:
    with st.spinner("Searching..."):
        try:
            response = client.search_standards(
                query=search_query,
                standard_types=standard_types if standard_types else None,
                categories=category_filter if category_filter else None,
                max_results=max_results
            )

            if response.success:
                results = response.data.get("results", [])
                total_count = response.data.get("total_count", len(results))
                st.session_state.search_results = results
                st.session_state.search_total = total_count
            else:
                st.error(f"Search failed: {response.error}")
                st.session_state.search_results = []
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            st.session_state.search_results = []

# Display results
if "search_results" in st.session_state:
    results = st.session_state.search_results
    total = st.session_state.get("search_total", len(results))

    if len(results) == 0:
        st.info("🔍 No results found. Try adjusting your search query or filters.")
    else:
        st.success(f"Found {total} results")

        # View type selector
        view_type = st.radio(
            "View as:",
            ["Cards", "List", "Table"],
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown("---")

        if view_type == "Cards":
            for result in results:
                with st.container():
                    r_col1, r_col2 = st.columns([4, 1])

                    with r_col1:
                        st.markdown(f"### {result.get('standard_code', '')} - {result.get('title', 'Untitled')}")
                        st.markdown(result.get("summary", result.get("description", "No description available")))

                        tag_col1, tag_col2, tag_col3 = st.columns(3)
                        with tag_col1:
                            st.caption(f"📁 {result.get('category', 'General')}")
                        with tag_col2:
                            relevance = result.get("relevance_score", 0)
                            if isinstance(relevance, (int, float)):
                                st.caption(f"🎯 Relevance: {relevance:.0%}")
                        with tag_col3:
                            sections = result.get("sections", [])
                            if sections:
                                st.caption(f"📄 {len(sections)} sections")

                    with r_col2:
                        if st.button("View Details", key=f"view_{result.get('standard_code', id(result))}", use_container_width=True):
                            st.session_state.selected_standard = result
                            st.info(f"Selected: {result.get('title', 'Standard')}")

                    st.markdown("---")

        elif view_type == "List":
            for idx, result in enumerate(results, 1):
                with st.expander(f"{idx}. {result.get('standard_code', '')} - {result.get('title', 'Untitled')}"):
                    st.markdown(f"**Description:** {result.get('summary', result.get('description', 'N/A'))}")
                    st.markdown(f"**Category:** {result.get('category', 'General')}")

                    relevance = result.get("relevance_score", 0)
                    if isinstance(relevance, (int, float)):
                        st.markdown(f"**Relevance:** {relevance:.0%}")

                    sections = result.get("sections", [])
                    if sections:
                        st.markdown("**Sections:**")
                        for section in sections[:5]:
                            st.markdown(f"- {section}")
                        if len(sections) > 5:
                            st.caption(f"...and {len(sections) - 5} more")

        else:  # Table view
            import pandas as pd

            table_data = pd.DataFrame([
                {
                    "Code": r.get("standard_code", ""),
                    "Title": r.get("title", "Untitled"),
                    "Category": r.get("category", "General"),
                    "Relevance": f"{r.get('relevance_score', 0):.0%}" if isinstance(r.get("relevance_score"), (int, float)) else "N/A"
                }
                for r in results
            ])

            st.dataframe(table_data, use_container_width=True, hide_index=True)

        # Export options
        st.markdown("---")
        exp_col1, exp_col2, exp_col3 = st.columns(3)

        with exp_col1:
            import pandas as pd
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Export CSV",
                csv,
                "search_results.csv",
                "text/csv",
                use_container_width=True
            )

        with exp_col2:
            if st.button("📋 Copy Results", use_container_width=True):
                st.info("Results copied to clipboard!")

        with exp_col3:
            if st.button("🔄 Clear Filters", use_container_width=True):
                st.session_state.search_results = None
                st.rerun()

else:
    # Initial state - show popular searches
    st.info("🔍 Enter a search query and apply filters to find relevant standards and documents.")

    st.markdown("### 🔥 Popular Searches")

    popular_searches = [
        ("Module Testing", "🔬"),
        ("Safety Standards", "🛡️"),
        ("Performance Tests", "📊"),
        ("Thermal Testing", "🌡️"),
        ("Grid Connection", "⚡"),
        ("Measurements", "📏")
    ]

    pop_cols = st.columns(3)

    for idx, (term, icon) in enumerate(popular_searches):
        with pop_cols[idx % 3]:
            if st.button(f"{icon} {term}", key=f"popular_{idx}", use_container_width=True):
                # Perform quick search
                try:
                    response = client.search_standards(query=term, max_results=20)
                    if response.success:
                        st.session_state.search_results = response.data.get("results", [])
                        st.session_state.search_total = response.data.get("total_count", 0)
                except Exception:
                    st.session_state.search_results = []
                st.rerun()

    # Quick reference
    st.markdown("---")
    st.markdown("### 📚 Quick Reference")

    ref_col1, ref_col2 = st.columns(2)

    with ref_col1:
        st.markdown("""
        **Common IEC Standards:**
        - **IEC 61215** - Module Design Qualification
        - **IEC 61730** - Module Safety
        - **IEC 62446** - Grid Connection
        - **IEC 60904** - Measurements
        - **IEC 61724** - Performance Monitoring
        """)

    with ref_col2:
        st.markdown("""
        **By Testing Phase:**
        - **Design**: IEC 61215, IEC 61853
        - **Safety**: IEC 61730, IEC 62109
        - **Installation**: IEC 62446
        - **Monitoring**: IEC 61724
        """)
