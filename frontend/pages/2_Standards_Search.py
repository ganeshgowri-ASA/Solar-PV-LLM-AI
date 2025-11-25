"""
Standards Search Page - Standalone Streamlit page
For use with Streamlit's multi-page app feature.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client

st.set_page_config(page_title="Standards Search - Solar PV AI", page_icon="", layout="wide")

st.title("Solar PV Standards Search")
st.markdown("Search through solar PV standards, codes, and regulations.")

client = get_client()

# Search input
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("Search Query", placeholder="e.g., safety, performance, installation...")
with col2:
    st.write("")
    st.write("")
    search = st.button("Search", type="primary", use_container_width=True)

# Filters
with st.expander("Filters"):
    try:
        categories_resp = client.get_categories()
        if categories_resp and categories_resp.success and categories_resp.data:
            categories = categories_resp.data
        else:
            categories = ["Safety", "Performance", "Installation", "Electrical", "Design", "Maintenance", "Grid Integration", "Testing", "Certification"]
    except Exception:
        categories = ["Safety", "Performance", "Installation", "Electrical", "Design", "Maintenance", "Grid Integration", "Testing", "Certification"]

    selected_cats = st.multiselect("Categories", categories)
    max_results = st.slider("Max Results", 5, 50, 10)

    # Standard type filter
    standard_types = ["IEC", "IEEE", "UL", "NFPA", "ASTM"]
    selected_types = st.multiselect("Standard Types", standard_types)

# Search
if search and query:
    with st.spinner("Searching..."):
        response = client.search_standards(
            query=query,
            standard_types=selected_types if selected_types else None,
            categories=selected_cats if selected_cats else None,
            max_results=max_results
        )

    if response.success:
        results = response.data.get("results", [])
        st.success(f"Found {response.data.get('total_count', 0)} results")

        for doc in results:
            with st.expander(f"{doc['standard_code']} - {doc['title']}"):
                st.markdown(f"**Category:** {doc['category']}")
                st.markdown(f"**Relevance:** {doc['relevance_score']:.0%}")
                if doc.get("summary"):
                    st.markdown("---")
                    st.markdown(doc["summary"])
                if doc.get("sections"):
                    st.markdown("**Sections:** " + ", ".join(doc["sections"]))
    else:
        st.error(response.error)

# Quick searches
st.markdown("---")
st.subheader("Quick Searches")
cols = st.columns(5)
quick_terms = ["Safety", "Performance", "Installation", "Inverter", "Grid"]
for i, term in enumerate(quick_terms):
    with cols[i]:
        if st.button(term, key=f"quick_{i}"):
            st.session_state["search_query"] = term
            st.rerun()
