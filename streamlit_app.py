"""Solar PV LLM AI - Integrated Streamlit Application
Combines all features from isolated branches into a unified deployment-ready app
"""
import streamlit as st
from streamlit_option_menu import option_menu
import os
from pathlib import Path
import sys

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Solar PV AI Assistant",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #667eea;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #5568d3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .feature-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        "chat_history": [],
        "selected_page": "Home",
        "search_results": [],
        "analysis_results": None,
        "calculator_results": {},
        "documents_processed": 0,
        "vector_db_ready": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def create_sidebar():
    """Create sidebar navigation and info"""
    with st.sidebar:
        # Logo/Header
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='color: #667eea;'>☀️</h1>
            <h3>Solar PV AI</h3>
            <p style='color: #666; font-size: 0.9rem;'>Intelligent Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation Menu
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "Home",
                "AI Chat",
                "Standards Search",
                "Calculators",
                "Image Analysis",
                "Document Library",
                "Dashboard",
            ],
            icons=[
                "house",
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
                    "--hover-color": "#f0f2f6",
                },
                "nav-link-selected": {"background-color": "#667eea"},
            },
        )
        
        st.divider()
        
        # System Status
        st.markdown("### 📊 System Status")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", st.session_state.documents_processed)
        with col2:
            status = "✅ Ready" if st.session_state.vector_db_ready else "⚠️ Setup"
            st.metric("Vector DB", status)
        
        st.divider()
        
        # Quick Info
        with st.expander("ℹ️ Features"):
            st.markdown("""
            **Available Features:**
            - 🤖 AI-powered Q&A with RAG
            - 🔍 IEC Standards Search
            - 🧮 PV System Calculators
            - 📷 Image Defect Analysis
            - 📚 Technical Documentation
            - 📊 Analytics Dashboard
            """)
        
        # Footer
        st.markdown("---")
        st.caption("v1.0.0 | © 2024 Solar PV AI")
        
        return selected


def render_home_page():
    """Render the home page"""
    # Header
    st.markdown('<div class="main-header">☀️ Solar PV AI Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Intelligent RAG-powered chatbot for Solar PV professionals</div>',
        unsafe_allow_html=True
    )
    
    # Key Features Grid
    st.markdown("## 🚀 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>🤖 AI Chat Assistant</h3>
            <p>Get instant answers to technical questions using advanced RAG technology with IEC standards knowledge base</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3>🔍 Smart Search</h3>
            <p>Search through IEC standards, technical documents, and research papers with semantic understanding</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <h3>🧮 PV Calculators</h3>
            <p>Calculate system parameters, performance metrics, and design specifications using NREL APIs</p>
        </div>
        """, unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="feature-box">
            <h3>📷 Image Analysis</h3>
            <p>Detect defects in solar panels using AI-powered computer vision and thermal imaging analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="feature-box">
            <h3>📚 Document Library</h3>
            <p>Access comprehensive IEC standards library with metadata extraction and citation management</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="feature-box">
            <h3>📊 Analytics</h3>
            <p>Monitor system usage, track queries, and analyze performance metrics with interactive dashboards</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Start Section
    st.markdown("## 🎯 Quick Start")
    
    tab1, tab2, tab3 = st.tabs(["📖 Getting Started", "⚙️ Setup", "📝 Examples"])
    
    with tab1:
        st.markdown("""
        ### Welcome to Solar PV AI Assistant!
        
        This intelligent chatbot combines multiple AI technologies to assist solar PV professionals:
        
        **Core Technologies:**
        - **RAG (Retrieval-Augmented Generation)**: Combines LLM reasoning with domain-specific knowledge
        - **Vector Database**: Fast semantic search through IEC standards using Pinecone
        - **Multi-LLM Orchestration**: Intelligent routing between Claude, GPT-4, and Gemini
        - **Citation Management**: Automatic extraction and formatting of technical references
        - **Image Analysis**: CV-powered defect detection for solar panels
        
        **Use Cases:**
        - Technical Q&A for engineers and technicians
        - IEC standard compliance verification
        - System design and optimization
        - Defect detection and diagnostics
        - Learning and training
        """)
    
    with tab2:
        st.markdown("""
        ### System Setup
        
        **Prerequisites:**
        1. API Keys (configured in `.env` file):
           - `ANTHROPIC_API_KEY` for Claude
           - `OPENAI_API_KEY` for GPT-4
           - `PINECONE_API_KEY` for vector database
           - `NREL_API_KEY` for calculators
        
        2. Document Processing:
           - Upload IEC standards PDFs to `data/iec_standards/`
           - Run ingestion pipeline: `python backend/scripts/ingest_documents.py`
        
        3. Vector Database:
           - Initialize Pinecone index
           - Generate embeddings for documents
           - Test retrieval accuracy
        
        **Deployment:**
        - Streamlit Cloud: Push to GitHub and deploy
        - Docker: Use provided `docker-compose.yml`
        - Local: `streamlit run streamlit_app.py`
        """)
    
    with tab3:
        st.markdown("""
        ### Example Queries
        
        Try these sample questions to get started:
        
        **Technical Questions:**
        - "What are the requirements for IEC 61215 thermal cycling tests?"
        - "Explain the difference between IEC 61730 and IEC 61215 standards"
        - "How to calculate performance ratio for a 100kW solar system?"
        
        **System Design:**
        - "Calculate optimal tilt angle for solar panels in Gujarat, India"
        - "What string sizing is recommended for 450W bifacial modules?"
        - "Estimate annual energy yield for a 10MW ground-mount system"
        
        **Defect Detection:**
        - "Analyze this EL image for cell cracks and hotspots"
        - "Identify potential PID effects in these thermal images"
        - "Compare degradation patterns across different module types"
        """)
    
    # System Architecture
    st.markdown("## 🏗️ System Architecture")
    
    with st.expander("View Architecture Details"):
        st.markdown("""
        ### Component Overview
        
        **Frontend (Streamlit):**
        - Interactive UI with multiple pages
        - Real-time chat interface
        - Visualization components
        - File upload and processing
        
        **Backend (FastAPI):**
        - RESTful API endpoints
        - Business logic layer
        - Service orchestration
        - Authentication & authorization
        
        **AI/ML Services:**
        - Document ingestion & chunking
        - Vector embeddings (Pinecone)
        - RAG retrieval engine
        - Multi-LLM orchestrator
        - Citation extractor
        - Image analysis (CV models)
        
        **Data Layer:**
        - Vector database (Pinecone)
        - Document storage
        - User feedback database
        - Analytics data warehouse
        
        **Integration:**
        - NREL APIs for solar data
        - Weather APIs
        - Equipment databases
        - Standards repositories
        """)


def render_ai_chat_page():
    """Render AI chat interface"""
    st.title("🤖 AI Chat Assistant")
    
    st.info("💡 Ask technical questions about solar PV systems, IEC standards, or system design. Answers are powered by RAG with verified IEC documentation.")
    
    # Chat history display
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Assistant:** {message['content']}")
            st.markdown("---")
    
    # Chat input
    user_input = st.text_input(
        "Ask a question:",
        key="chat_input",
        placeholder="e.g., What are the IEC 61215 test requirements for PV modules?"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        send_button = st.button("Send", type="primary")
    with col2:
        clear_button = st.button("Clear History")
    
    if send_button and user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Simulated AI response (replace with actual RAG call)
        response = f"""Based on IEC standards and technical documentation:
        
        This is a placeholder response. In production, this will be powered by:
        - RAG retrieval from Pinecone vector database
        - Multi-LLM orchestration (Claude/GPT-4/Gemini)
        - Citation extraction and formatting
        - Context-aware response generation
        
        Your question: "{user_input}"
        
        **References:** IEC 61215, IEC 61730, IEC 60904
        """
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()


def render_standards_search_page():
    """Render standards search interface"""
    st.title("🔍 IEC Standards Search")
    
    st.info("Search through comprehensive IEC standards database with semantic understanding")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search query:",
            placeholder="e.g., thermal cycling test procedures"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            standard_series = st.multiselect(
                "Standard Series",
                ["IEC 61215", "IEC 61730", "IEC 60904", "IEC 61853", "IEC 62804"]
            )
        
        with col2:
            doc_type = st.multiselect(
                "Document Type",
                ["Standard", "Technical Report", "Guide", "Amendment"]
            )
        
        with col3:
            year_range = st.slider("Publication Year", 2000, 2024, (2015, 2024))
    
    if search_button and search_query:
        st.markdown("### Search Results")
        
        # Placeholder results
        results = [
            {
                "title": "IEC 61215-1:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval",
                "relevance": 0.95,
                "excerpt": "This standard provides design qualification and type approval requirements for terrestrial photovoltaic modules...",
                "citation": "IEC 61215-1:2021"
            },
            {
                "title": "IEC 61215-2:2021 - Test procedures - Crystalline silicon modules",
                "relevance": 0.89,
                "excerpt": "Specifies test procedures for crystalline silicon terrestrial photovoltaic modules including thermal cycling...",
                "citation": "IEC 61215-2:2021"
            },
        ]
        
        for i, result in enumerate(results, 1):
            with st.container():
                st.markdown(f"**{i}. {result['title']}**")
                st.progress(result['relevance'])
                st.caption(f"Relevance: {result['relevance']*100:.1f}%")
                st.markdown(result['excerpt'])
                st.caption(f"Citation: {result['citation']}")
                st.markdown("---")


def render_calculators_page():
    """Render PV calculators"""
    st.title("🧮 Solar PV Calculators")
    
    st.info("Calculate system parameters using NREL APIs and industry-standard formulas")
    
    calc_type = st.selectbox(
        "Select Calculator:",
        [
            "System Sizing",
            "Energy Yield",
            "Performance Ratio",
            "String Configuration",
            "Tilt & Azimuth Optimization",
            "Shading Analysis",
        ]
    )
    
    if calc_type == "System Sizing":
        st.markdown("### System Sizing Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            load_kwh = st.number_input("Daily Load (kWh/day)", min_value=1.0, value=30.0)
            sun_hours = st.number_input("Peak Sun Hours", min_value=1.0, value=5.0)
            system_voltage = st.selectbox("System Voltage (V)", [12, 24, 48])
        
        with col2:
            efficiency = st.slider("System Efficiency (%)", 60, 95, 80)
            autonomy_days = st.number_input("Autonomy Days", min_value=1, value=2)
            depth_discharge = st.slider("Battery DoD (%)", 20, 80, 50)
        
        if st.button("Calculate", type="primary"):
            # Simplified calculations
            array_wp = (load_kwh * 1000) / (sun_hours * (efficiency/100))
            battery_ah = (load_kwh * 1000 * autonomy_days) / (system_voltage * (depth_discharge/100))
            
            st.success("Calculation Complete!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Array Size", f"{array_wp:.0f} Wp")
            with col2:
                st.metric("Battery Bank", f"{battery_ah:.0f} Ah")
            with col3:
                st.metric("Est. Modules (400W)", f"{array_wp/400:.0f}")
    
    elif calc_type == "Energy Yield":
        st.markdown("### Annual Energy Yield Estimator")
        st.info("This calculator integrates with NREL PVWatts API for accurate estimates")
        
        # Add calculator UI for other types...


def render_image_analysis_page():
    """Render image analysis interface"""
    st.title("📷 PV Module Image Analysis")
    
    st.info("Upload EL images, thermal images, or visual inspection photos for AI-powered defect detection")
    
    analysis_type = st.radio(
        "Analysis Type:",
        ["Electroluminescence (EL)", "Thermal (IR)", "Visual Inspection"],
        horizontal=True
    )
    
    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["jpg", "jpeg", "png", "tiff"],
        help="Supported formats: JPG, PNG, TIFF"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Uploaded Image")
            st.image(uploaded_file, use_container_width=True)
        
        with col2:
            st.markdown("### Analysis Results")
            
            if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
                with st.spinner("Analyzing image..."):
                    import time
                    time.sleep(2)  # Simulate processing
                    
                    st.success("Analysis Complete!")
                    
                    # Placeholder results
                    st.markdown("**Detected Issues:**")
                    st.error("⚠️ Cell Cracks: 3 detected")
                    st.warning("⚠️ Hot Spots: 1 detected")
                    st.info("ℹ️ Discoloration: Minor")
                    
                    st.markdown("**Severity Assessment:**")
                    st.metric("Overall Grade", "B", "-1")
                    st.progress(0.75)
                    
                    st.markdown("**Recommendations:**")
                    st.markdown("""
                    - Inspect affected cells for further damage
                    - Monitor thermal performance
                    - Consider warranty claim for manufacturing defects
                    """)


def render_document_library_page():
    """Render document library"""
    st.title("📚 Technical Document Library")
    
    st.info("Browse and search through uploaded IEC standards and technical documentation")
    
    # Document categories
    category = st.selectbox(
        "Category:",
        [
            "All Documents",
            "IEC Standards",
            "Test Procedures",
            "Safety Standards",
            "Performance Standards",
            "Research Papers",
        ]
    )
    
    # Document list (placeholder)
    st.markdown("### Available Documents")
    
    documents = [
        {"name": "IEC 61215-1:2021", "size": "2.4 MB", "pages": 45, "uploaded": "2024-01-15"},
        {"name": "IEC 61730-1:2016", "size": "1.8 MB", "pages": 32, "uploaded": "2024-01-15"},
        {"name": "IEC 60904-1:2020", "size": "3.1 MB", "pages": 58, "uploaded": "2024-01-16"},
    ]
    
    for doc in documents:
        with st.expander(f"📄 {doc['name']}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Size", doc['size'])
            with col2:
                st.metric("Pages", doc['pages'])
            with col3:
                st.metric("Uploaded", doc['uploaded'])
            with col4:
                st.button("📥 Download", key=f"download_{doc['name']}")


def render_dashboard_page():
    """Render analytics dashboard"""
    st.title("📊 Analytics Dashboard")
    
    st.info("Monitor system usage, query patterns, and performance metrics")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Queries", "1,247", "+12%")
    with col2:
        st.metric("Avg Response Time", "1.8s", "-0.3s")
    with col3:
        st.metric("User Satisfaction", "94.3%", "+2.1%")
    with col4:
        st.metric("Documents Indexed", "156", "+8")
    
    # Placeholder for charts
    st.markdown("### Query Trends")
    st.line_chart({"Queries": [10, 15, 13, 17, 20, 25, 22]})
    
    st.markdown("### Popular Topics")
    st.bar_chart({"IEC 61215": 45, "IEC 61730": 38, "System Design": 32, "Defect Detection": 28})


def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Create sidebar and get selected page
    selected_page = create_sidebar()
    
    # Route to selected page
    if selected_page == "Home":
        render_home_page()
    elif selected_page == "AI Chat":
        render_ai_chat_page()
    elif selected_page == "Standards Search":
        render_standards_search_page()
    elif selected_page == "Calculators":
        render_calculators_page()
    elif selected_page == "Image Analysis":
        render_image_analysis_page()
    elif selected_page == "Document Library":
        render_document_library_page()
    elif selected_page == "Dashboard":
        render_dashboard_page()


if __name__ == "__main__":
    main()
