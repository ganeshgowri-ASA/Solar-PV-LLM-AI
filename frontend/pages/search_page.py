"""
Advanced Search Page
Search IEC standards and technical documents with filters
"""
import streamlit as st
from backend.api.mock_service import mock_api
from frontend.utils.ui_components import (
    show_loading,
    show_empty_state,
    create_card,
)
from config.settings import IEC_STANDARDS, TEST_TYPES


def render():
    """Render the search page"""
    st.title("🔍 Advanced Search")
    st.markdown(
        "Search through IEC standards, technical documents, and testing procedures "
        "with advanced filtering options."
    )

    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search",
            placeholder="Enter keywords: e.g., 'thermal cycling', 'module safety', 'IEC 61215'",
            label_visibility="collapsed",
        )
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")

    st.divider()

    # Filters in columns
    st.markdown("### 🎯 Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        category_filter = st.multiselect(
            "Categories",
            options=[
                "Module Testing",
                "Safety",
                "Performance",
                "Systems",
                "Measurements",
            ],
            default=[],
        )

    with filter_col2:
        difficulty_filter = st.multiselect(
            "Difficulty Level",
            options=["Beginner", "Intermediate", "Advanced"],
            default=[],
        )

    with filter_col3:
        sort_by = st.selectbox(
            "Sort By",
            options=["Relevance", "Title (A-Z)", "Title (Z-A)", "Most Recent"],
            index=0,
        )

    # Additional filters in expander
    with st.expander("🔧 More Filters"):
        filter_col4, filter_col5 = st.columns(2)

        with filter_col4:
            test_type_filter = st.multiselect(
                "Test Types",
                options=TEST_TYPES,
                default=[],
            )

        with filter_col5:
            min_sections = st.slider(
                "Minimum Sections",
                min_value=1,
                max_value=20,
                value=1,
            )

    st.divider()

    # Perform search
    if search_button or search_query:
        with show_loading("Searching..."):
            results = mock_api.search_standards(
                query=search_query,
                categories=category_filter if category_filter else None,
                difficulty=difficulty_filter if difficulty_filter else None,
            )

            # Apply additional filters
            if min_sections > 1:
                results = [r for r in results if r["test_count"] >= min_sections]

            # Store results in session state
            st.session_state.search_results = results

    # Display results
    if hasattr(st.session_state, "search_results"):
        results = st.session_state.search_results

        if len(results) == 0:
            show_empty_state(
                title="No Results Found",
                message="Try adjusting your search query or filters.",
                icon="🔍",
            )
        else:
            # Results header
            st.markdown(f"### 📊 Results ({len(results)} found)")

            # Display type selector
            view_type = st.radio(
                "View as:",
                ["Cards", "List", "Table"],
                horizontal=True,
                label_visibility="collapsed",
            )

            st.divider()

            if view_type == "Cards":
                # Card view
                for result in results:
                    with st.container():
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.markdown(
                                f"""
                                <div class="dashboard-card">
                                    <h3 style="margin: 0 0 0.5rem 0; color: #333;">
                                        {result['title']}
                                    </h3>
                                    <p style="color: #666; margin: 0 0 0.75rem 0;">
                                        {result['description']}
                                    </p>
                                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                                        <span class="status-badge status-online">
                                            📁 {result['category']}
                                        </span>
                                        <span class="status-badge" style="background-color: #e3f2fd; color: #0d47a1;">
                                            📊 {result['test_count']} tests
                                        </span>
                                        <span class="status-badge" style="background-color: #f3e5f5; color: #4a148c;">
                                            🎯 {result['difficulty']}
                                        </span>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        with col2:
                            if st.button(
                                "View Details",
                                key=f"view_{result['id']}",
                                use_container_width=True,
                            ):
                                st.session_state.selected_standard = result["id"]
                                st.session_state.selected_page = "Standards Library"
                                st.rerun()

            elif view_type == "List":
                # List view
                for idx, result in enumerate(results, 1):
                    with st.expander(
                        f"{idx}. {result['title']} - {result['category']}", expanded=False
                    ):
                        st.markdown(f"**Description:** {result['description']}")
                        st.markdown(f"**Category:** {result['category']}")
                        st.markdown(f"**Difficulty:** {result['difficulty']}")
                        st.markdown(f"**Number of Tests:** {result['test_count']}")

                        st.markdown("**Key Sections:**")
                        for section in result["sections"][:5]:
                            st.markdown(f"- {section}")

                        if len(result["sections"]) > 5:
                            st.caption(f"...and {len(result['sections']) - 5} more")

                        if st.button(
                            "View Full Standard",
                            key=f"list_view_{result['id']}",
                            use_container_width=True,
                        ):
                            st.session_state.selected_standard = result["id"]
                            st.session_state.selected_page = "Standards Library"
                            st.rerun()

            else:  # Table view
                import pandas as pd

                table_data = pd.DataFrame(
                    [
                        {
                            "Title": r["title"],
                            "Category": r["category"],
                            "Tests": r["test_count"],
                            "Difficulty": r["difficulty"],
                        }
                        for r in results
                    ]
                )

                st.dataframe(
                    table_data,
                    use_container_width=True,
                    hide_index=True,
                )

            # Export results
            st.divider()
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📥 Export as CSV", use_container_width=True):
                    import pandas as pd

                    df = pd.DataFrame(results)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        "search_results.csv",
                        "text/csv",
                        use_container_width=True,
                    )

            with col2:
                if st.button("📋 Copy Results", use_container_width=True):
                    st.info("Results copied to clipboard!")

            with col3:
                if st.button("🔄 Clear Filters", use_container_width=True):
                    st.rerun()

    else:
        # Initial state
        show_empty_state(
            title="Start Searching",
            message="Enter a search query and apply filters to find relevant IEC standards and documents.",
            icon="🔍",
        )

        # Show popular searches
        st.markdown("### 🔥 Popular Searches")
        popular_col1, popular_col2, popular_col3 = st.columns(3)

        popular_searches = [
            ("Module Testing", "🔬"),
            ("Safety Standards", "🛡️"),
            ("Performance Tests", "📊"),
            ("Thermal Testing", "🌡️"),
            ("Grid Connection", "⚡"),
            ("Measurements", "📏"),
        ]

        for idx, (search_term, icon) in enumerate(popular_searches):
            col = [popular_col1, popular_col2, popular_col3][idx % 3]
            with col:
                if st.button(
                    f"{icon} {search_term}",
                    key=f"popular_{idx}",
                    use_container_width=True,
                ):
                    results = mock_api.search_standards(query=search_term)
                    st.session_state.search_results = results
                    st.rerun()
