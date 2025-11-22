"""
Image Analysis Page
Upload and analyze solar panel images for defects and performance issues
"""
import streamlit as st
from backend.api.mock_service import mock_api
from frontend.utils.ui_components import (
    show_loading,
    show_success,
    show_error,
    show_info,
    create_file_uploader,
)
from config.settings import MAX_FILE_SIZE_MB


def render():
    """Render the image analysis page"""
    st.title("🔬 Image Analysis")
    st.markdown(
        "Upload solar panel images for AI-powered defect detection, thermal analysis, "
        "and performance assessment."
    )

    # Information cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="dashboard-card">
                <h4>📷 Visual Inspection</h4>
                <p>Detect physical defects, cracks, and discoloration</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="dashboard-card">
                <h4>🌡️ Thermal Analysis</h4>
                <p>Identify hot-spots and thermal anomalies</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="dashboard-card">
                <h4>⚡ Performance</h4>
                <p>Estimate power loss and degradation</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # File upload section
    st.markdown("### 📤 Upload Image")

    upload_col1, upload_col2 = st.columns([2, 1])

    with upload_col1:
        uploaded_file = create_file_uploader(
            label="Choose an image",
            accepted_types=["png", "jpg", "jpeg", "bmp", "tiff"],
            max_size_mb=MAX_FILE_SIZE_MB,
            help_text="Supported formats: PNG, JPG, JPEG, BMP, TIFF",
            key="image_upload",
        )

    with upload_col2:
        st.markdown("### Analysis Options")
        analysis_type = st.selectbox(
            "Analysis Type",
            [
                "Comprehensive",
                "Visual Only",
                "Thermal Only",
                "Performance Only",
            ],
            index=0,
        )

        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="Minimum confidence level for defect detection",
        )

    # Display uploaded image
    if uploaded_file is not None:
        st.divider()

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🖼️ Original Image")
            st.image(uploaded_file, use_container_width=True)

            # Image metadata
            with st.expander("📋 Image Information"):
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
                st.write(f"**Type:** {uploaded_file.type}")

        with col2:
            st.markdown("### 🔍 Analysis")

            # Analyze button
            if st.button(
                "🚀 Start Analysis",
                type="primary",
                use_container_width=True,
            ):
                with show_loading("Analyzing image... This may take a moment."):
                    analysis_results = mock_api.analyze_image(uploaded_file)

                # Store results in session state
                st.session_state.analysis_results = analysis_results
                show_success("Analysis completed successfully!")
                st.rerun()

    # Display analysis results
    if hasattr(st.session_state, "analysis_results") and st.session_state.analysis_results:
        results = st.session_state.analysis_results

        if results["status"] == "success":
            st.divider()
            st.markdown("### 📊 Analysis Results")

            analysis_data = results["analysis"]

            # Overview metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric(
                    "Module Type",
                    analysis_data["module_type"],
                )

            with metric_col2:
                st.metric(
                    "Overall Health",
                    analysis_data["overall_health"],
                    help="General condition assessment",
                )

            with metric_col3:
                st.metric(
                    "Defects Found",
                    len(analysis_data["detected_defects"]),
                )

            with metric_col4:
                st.metric(
                    "Est. Power Loss",
                    analysis_data["estimated_power_loss"],
                    delta=f"-{analysis_data['estimated_power_loss']}",
                    delta_color="inverse",
                )

            # Detected defects
            if analysis_data["detected_defects"]:
                st.markdown("### 🔴 Detected Defects")

                for idx, defect in enumerate(analysis_data["detected_defects"], 1):
                    severity_color = {
                        "High": "#f8d7da",
                        "Medium": "#fff3cd",
                        "Low": "#d1ecf1",
                    }

                    with st.expander(
                        f"Defect {idx}: {defect['type']} - {defect['severity']} Severity",
                        expanded=True,
                    ):
                        defect_col1, defect_col2, defect_col3 = st.columns(3)

                        with defect_col1:
                            st.write(f"**Type:** {defect['type']}")
                            st.write(f"**Location:** {defect['location']}")

                        with defect_col2:
                            st.write(f"**Severity:** {defect['severity']}")
                            st.progress(
                                defect["confidence"],
                                text=f"Confidence: {defect['confidence']:.0%}",
                            )

                        with defect_col3:
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: {severity_color.get(defect['severity'], '#f8f9fa')};
                                    padding: 1rem;
                                    border-radius: 0.5rem;
                                    border-left: 4px solid #dc3545;
                                ">
                                    <strong>Impact:</strong><br>
                                    {'High priority - Immediate attention required' if defect['severity'] == 'High'
                                    else 'Medium priority - Monitor and plan maintenance' if defect['severity'] == 'Medium'
                                    else 'Low priority - Minor issue, routine check'}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
            else:
                show_success("✅ No defects detected! Module appears to be in good condition.")

            # Recommendations
            st.markdown("### 💡 Recommendations")

            for idx, recommendation in enumerate(
                analysis_data["recommendations"], 1
            ):
                st.markdown(
                    f"""
                    <div style="
                        background-color: #d1ecf1;
                        border-left: 4px solid #17a2b8;
                        padding: 1rem;
                        margin: 0.5rem 0;
                        border-radius: 0.25rem;
                    ">
                        <strong>{idx}.</strong> {recommendation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Action buttons
            st.divider()
            action_col1, action_col2, action_col3 = st.columns(3)

            with action_col1:
                if st.button(
                    "📥 Download Report",
                    use_container_width=True,
                ):
                    # Generate report text
                    report = f"""
SOLAR PANEL IMAGE ANALYSIS REPORT
{'='*50}

MODULE INFORMATION:
- Type: {analysis_data['module_type']}
- Overall Health: {analysis_data['overall_health']}
- Estimated Power Loss: {analysis_data['estimated_power_loss']}

DETECTED DEFECTS ({len(analysis_data['detected_defects'])}):
"""
                    for idx, defect in enumerate(
                        analysis_data["detected_defects"], 1
                    ):
                        report += f"""
{idx}. {defect['type']}
   - Location: {defect['location']}
   - Severity: {defect['severity']}
   - Confidence: {defect['confidence']:.0%}
"""

                    report += f"""

RECOMMENDATIONS:
"""
                    for idx, rec in enumerate(
                        analysis_data["recommendations"], 1
                    ):
                        report += f"{idx}. {rec}\n"

                    report += f"""

Analysis Timestamp: {results['timestamp']}
"""

                    st.download_button(
                        "Download",
                        report,
                        "analysis_report.txt",
                        "text/plain",
                        use_container_width=True,
                    )

            with action_col2:
                if st.button(
                    "🔄 Analyze Another",
                    use_container_width=True,
                ):
                    st.session_state.analysis_results = None
                    st.rerun()

            with action_col3:
                if st.button(
                    "💬 Ask AI About Results",
                    use_container_width=True,
                ):
                    st.session_state.selected_page = "Chat"
                    st.rerun()

        else:
            show_error("Analysis failed. Please try again with a different image.")

    else:
        # No image uploaded yet
        st.divider()

        st.markdown("### 📚 Analysis Capabilities")

        cap_col1, cap_col2 = st.columns(2)

        with cap_col1:
            st.markdown(
                """
                **Visual Defects:**
                - ✅ Micro-cracks in cells
                - ✅ Discoloration and browning
                - ✅ Snail trails
                - ✅ Cell interconnect failures
                - ✅ Delamination
                - ✅ Physical damage
                """
            )

        with cap_col2:
            st.markdown(
                """
                **Thermal Anomalies:**
                - 🌡️ Hot-spots
                - 🌡️ Bypass diode issues
                - 🌡️ Shading problems
                - 🌡️ Soiling and dirt
                - 🌡️ Junction box defects
                - 🌡️ String mismatch
                """
            )

        st.divider()

        # Sample images
        st.markdown("### 🖼️ Sample Analysis")
        st.info(
            "Upload an image of a solar panel or module to get started. "
            "For best results, ensure good lighting and capture the entire module."
        )

        sample_col1, sample_col2, sample_col3 = st.columns(3)

        with sample_col1:
            st.markdown("**✅ Good Image**")
            st.caption(
                "Well-lit, clear, full module visible"
            )

        with sample_col2:
            st.markdown("**⚠️ Acceptable Image**")
            st.caption(
                "Partial view, some glare"
            )

        with sample_col3:
            st.markdown("**❌ Poor Image**")
            st.caption(
                "Too dark, blurry, obstructed"
            )
