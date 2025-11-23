"""
Custom CSS styles for Solar PV LLM AI System
"""

def get_custom_css():
    """Return custom CSS for the application"""
    return """
    <style>
    /* Main Container Styling */
    .main {
        padding: 1rem;
    }

    /* Responsive font sizes */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
    }

    /* Card Styling */
    .stCard {
        padding: 1.5rem;
        border-radius: 0.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
        margin-bottom: 1rem;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 0.5rem;
        transition: all 0.3s ease;
        font-weight: 500;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Primary Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
    }

    /* Input Field Styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        font-weight: 500;
    }

    .streamlit-expanderHeader:hover {
        background-color: #e9ecef;
    }

    /* Chat Message Styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 0.5rem;
    }

    /* Metric Styling */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }

    /* File Uploader Styling */
    .uploadedFile {
        border-radius: 0.5rem;
        border: 2px dashed #667eea;
        padding: 1rem;
    }

    /* Progress Bar Styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 1rem;
    }

    /* Table Styling */
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden;
    }

    .dataframe thead tr th {
        background-color: #667eea;
        color: white;
        font-weight: 600;
    }

    .dataframe tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    .dataframe tbody tr:hover {
        background-color: #e9ecef;
    }

    /* Alert Styling */
    .stAlert {
        border-radius: 0.5rem;
        border-left-width: 4px;
    }

    /* Success Alert */
    .stSuccess {
        background-color: #d4edda;
        border-left-color: #28a745;
    }

    /* Error Alert */
    .stError {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }

    /* Warning Alert */
    .stWarning {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }

    /* Info Alert */
    .stInfo {
        background-color: #d1ecf1;
        border-left-color: #17a2b8;
    }

    /* Loading Spinner */
    .stSpinner > div {
        border-color: #667eea;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Responsive Grid */
    @media (max-width: 768px) {
        .row-widget.stRadio > div {
            flex-direction: column;
        }
        .row-widget.stCheckbox > div {
            flex-direction: column;
        }
    }

    /* Citation Styling */
    .citation {
        background-color: #f8f9fa;
        border-left: 3px solid #667eea;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
        font-size: 0.9rem;
    }

    .citation-title {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.25rem;
    }

    .citation-excerpt {
        color: #666;
        font-style: italic;
    }

    /* Dashboard Card */
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .dashboard-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .status-online {
        background-color: #d4edda;
        color: #155724;
    }

    .status-warning {
        background-color: #fff3cd;
        color: #856404;
    }

    .status-offline {
        background-color: #f8d7da;
        color: #721c24;
    }

    /* Accessibility Improvements */
    button:focus,
    input:focus,
    select:focus,
    textarea:focus {
        outline: 2px solid #667eea;
        outline-offset: 2px;
    }

    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        .stCard {
            background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        }

        .dashboard-card {
            background: #2d3748;
            color: #e2e8f0;
        }
    }

    /* Print Styles */
    @media print {
        .stButton,
        .stDownloadButton,
        .stSidebar {
            display: none !important;
        }
    }
    </style>
    """
