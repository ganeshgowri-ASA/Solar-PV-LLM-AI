"""
Image Analysis Page - Standalone Streamlit page
For use with Streamlit's multi-page app feature.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client

st.set_page_config(page_title="Image Analysis - Solar PV AI", page_icon="", layout="wide")

st.title("Solar Panel Image Analysis")
st.markdown("Upload images of solar panels for AI-powered analysis.")

client = get_client()

# Upload
uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp"])

# Options
col1, col2 = st.columns(2)
with col1:
    analysis_type = st.selectbox(
        "Analysis Type",
        [
            ("General Analysis", "general"),
            ("Defect Detection", "defect_detection"),
            ("Shading Analysis", "shading"),
            ("Layout Analysis", "layout")
        ],
        format_func=lambda x: x[0]
    )
with col2:
    include_recs = st.checkbox("Include Recommendations", value=True)

if uploaded:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Uploaded Image")
        st.image(uploaded, use_container_width=True)

    with col2:
        st.subheader("Analysis Results")

        if st.button("Analyze", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                response = client.analyze_image(
                    uploaded.getvalue(),
                    analysis_type[1],
                    include_recs
                )

            if response.success:
                data = response.data

                st.metric("Confidence", f"{data.get('confidence_score', 0):.0%}")
                st.markdown("---")
                st.markdown(data.get("analysis", "No analysis available"))

                if data.get("detected_elements"):
                    st.markdown("---")
                    st.subheader("Detected")
                    for elem in data["detected_elements"]:
                        st.markdown(f"- {elem.get('type')}: {elem.get('confidence', 0):.0%}")

                if data.get("issues_found"):
                    st.markdown("---")
                    st.subheader("Issues")
                    for issue in data["issues_found"]:
                        if issue.get("severity") == "warning":
                            st.warning(issue.get("description"))
                        elif issue.get("severity") == "error":
                            st.error(issue.get("description"))
                        else:
                            st.info(issue.get("description"))

                if include_recs and data.get("recommendations"):
                    st.markdown("---")
                    st.subheader("Recommendations")
                    for rec in data["recommendations"]:
                        st.success(rec)
            else:
                st.error(response.error)

# Tips
st.markdown("---")
st.subheader("Tips for Better Analysis")
tips = [
    "Use high-resolution images",
    "Include full solar array in frame",
    "Take photos during daylight",
    "Capture multiple angles"
]
for tip in tips:
    st.markdown(f"- {tip}")
