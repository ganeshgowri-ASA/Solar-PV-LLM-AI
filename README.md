# Solar PV LLM AI System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-FF4B4B)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**An AI-powered technical assistant for solar PV systems with RAG, citation-backed responses, and comprehensive analysis tools.**

Repository for developing Solar PV AI LLM system with incremental training, RAG (Retrieval-Augmented Generation), citation support, and autonomous delivery. Built for broad audiences from beginners to experts.

---

## Features

### 🤖 AI Chat Assistant
- **Conversational AI** powered by GPT-4 for technical Q&A
- **RAG (Retrieval-Augmented Generation)** for accurate, source-backed answers
- **Citation System** with page numbers, sections, and relevance scores
- **Context-aware responses** about IEC standards, testing, and best practices
- **Export chat history** for documentation and reporting

### 🔍 Advanced Search
- **Filter by category**: Module Testing, Safety, Performance, Systems, Measurements
- **Difficulty levels**: Beginner, Intermediate, Advanced
- **Multiple view modes**: Cards, List, Table
- **Export results** as CSV for further analysis
- **Related standards** discovery

### 🧮 Professional Calculators
- **Energy Yield Calculator**: Estimate daily, monthly, and annual production
- **System Sizing Calculator**: Determine optimal system size and panel count
- **ROI Calculator**: Calculate payback period and 25-year returns
- **Efficiency Calculator**: Analyze module and system efficiency
- **Shading Analysis**: Estimate losses from shading throughout the day

### 🔬 Image Analysis
- **AI-powered defect detection**: Micro-cracks, hot-spots, discoloration
- **Thermal anomaly identification**: Hot-spots, bypass diode issues
- **Performance assessment**: Estimated power loss calculations
- **Automated recommendations** for maintenance and repairs
- **Downloadable reports** with detailed findings

### 📚 Standards Library
- **Comprehensive IEC standards database**
- **Detailed section breakdowns** for each standard
- **Related standards** cross-referencing
- **AI question capability** for standard-specific queries
- **Version tracking** and status information

### 📊 Dashboard Analytics
- **System health monitoring**: Uptime, response times, active queries
- **Usage statistics**: Query volume, success rates, performance trends
- **Knowledge base metrics**: Document count, index size, last update
- **Time series visualizations**: 30-day performance trends
- **Activity logs** and real-time monitoring

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (for cloning the repository)

### Step 1: Clone the Repository
```bash
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required: OPENAI_API_KEY
```

### Step 5: Run the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

---

## Project Structure

```
Solar-PV-LLM-AI/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── README.md                       # This file
│
├── frontend/                       # Frontend application
│   ├── pages/                      # Page modules
│   │   ├── chat_page.py           # AI chat interface
│   │   ├── search_page.py         # Advanced search
│   │   ├── calculators_page.py    # Solar calculators
│   │   ├── image_analysis_page.py # Image analysis
│   │   ├── standards_library_page.py # Standards browser
│   │   └── dashboard_page.py      # Analytics dashboard
│   │
│   ├── components/                 # Reusable UI components
│   │
│   └── utils/                      # Utility functions
│       ├── ui_components.py       # UI helper components
│       └── styles.py              # Custom CSS styles
│
├── backend/                        # Backend services
│   ├── api/                        # API services
│   │   └── mock_service.py        # Mock API (for development)
│   │
│   └── models/                     # Data models
│
├── config/                         # Configuration
│   └── settings.py                # Application settings
│
├── tests/                          # Test suite
│
├── docs/                           # Documentation
│
└── assets/                         # Static assets
```

---

## Usage Guide

### Chat Interface
1. Navigate to **Chat** from the sidebar
2. Type your question in the chat input
3. View AI response with sources and citations
4. Click on expandable sections to see source details
5. Use suggested questions for quick queries
6. Export chat history for documentation

### Advanced Search
1. Navigate to **Search** from the sidebar
2. Enter search keywords
3. Apply filters (category, difficulty, test types)
4. Choose view mode (Cards, List, or Table)
5. Click "View Details" to see full standard information
6. Export results as CSV

### Calculators
1. Navigate to **Calculators** from the sidebar
2. Select the calculator tab you need
3. Enter your parameters
4. Click "Calculate" to see results
5. View interactive charts and visualizations
6. Adjust parameters to see real-time updates

### Image Analysis
1. Navigate to **Image Analysis** from the sidebar
2. Upload a solar panel image (PNG, JPG, etc.)
3. Select analysis type (Comprehensive, Visual, Thermal, or Performance)
4. Click "Start Analysis"
5. Review detected defects and recommendations
6. Download the analysis report

### Standards Library
1. Navigate to **Standards Library** from the sidebar
2. Browse by category or view all standards
3. Click "View Details" for in-depth information
4. Explore sections and related standards
5. Ask AI questions about specific standards
6. Download standard summaries

### Dashboard
1. Navigate to **Dashboard** from the sidebar
2. View real-time system health metrics
3. Monitor usage statistics and trends
4. Analyze 30-day performance charts
5. Check recent activity logs
6. Export metrics and reports

---

## Configuration

### Environment Variables

Edit `.env` file to configure:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here

# Application Settings
APP_NAME=Solar PV LLM AI System
APP_VERSION=1.0.0
DEBUG_MODE=False

# Backend API
BACKEND_URL=http://localhost:8000
API_TIMEOUT=30

# File Upload Settings
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,docx,pptx,png,jpg,jpeg

# RAG Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# LLM Settings
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_TOKENS=2000
```

---

## Technology Stack

### Frontend
- **Streamlit**: Interactive web application framework
- **Plotly**: Interactive data visualizations
- **Pandas**: Data manipulation and analysis
- **streamlit-option-menu**: Enhanced navigation menu

### AI/ML
- **OpenAI GPT-4**: Language model for chat
- **LangChain**: RAG framework
- **Sentence Transformers**: Text embeddings
- **FAISS**: Vector similarity search

### Backend
- **Python**: Core programming language
- **Requests/HTTPX**: HTTP client libraries

### Image Processing
- **Pillow**: Image manipulation
- **OpenCV**: Computer vision

---

## Development

### Running Tests
```bash
pytest tests/ -v --cov
```

### Code Formatting
```bash
black .
flake8 .
```

### Adding New Features

1. Create new page module in `frontend/pages/`
2. Add route in `app.py`
3. Add navigation item in sidebar
4. Implement page rendering logic
5. Test and document

---

## API Integration

The application uses a mock API service for development. To integrate with a real backend:

1. Replace `backend/api/mock_service.py` with real API client
2. Update `BACKEND_URL` in `.env`
3. Implement authentication if required
4. Handle API rate limiting and errors

Example API client structure:
```python
class RealAPIService:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def chat_completion(self, message, include_sources=True):
        # Implement real API call
        pass
```

---

## Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Add secrets in Streamlit dashboard
4. Deploy

### Docker
```bash
# Build image
docker build -t solar-pv-ai .

# Run container
docker run -p 8501:8501 solar-pv-ai
```

### Manual Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run with nohup
nohup streamlit run app.py --server.port 8501 &
```

---

## Accessibility

The application is built with accessibility in mind:

- ✅ Keyboard navigation support
- ✅ Screen reader compatible
- ✅ High contrast color schemes
- ✅ Responsive design for all devices
- ✅ ARIA labels and semantic HTML
- ✅ Focus indicators for interactive elements

---

## Browser Compatibility

Tested and supported on:
- Google Chrome (latest)
- Mozilla Firefox (latest)
- Safari (latest)
- Microsoft Edge (latest)

Mobile browsers:
- iOS Safari
- Chrome Mobile
- Samsung Internet

---

## Performance

### Optimization Features
- Lazy loading of components
- Caching of API responses
- Efficient data serialization
- Minimized re-renders
- Compressed assets

### Performance Targets
- Initial load: < 2 seconds
- Chat response: < 300ms
- Search results: < 500ms
- Image analysis: < 2 seconds

---

## Security

### Best Practices Implemented
- Environment variable for sensitive data
- Input validation and sanitization
- File upload size limits
- HTTPS recommended for production
- API key protection
- CORS configuration

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

For questions, issues, or feature requests:

- **GitHub Issues**: [Report a bug](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues)
- **Documentation**: [Wiki](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/wiki)
- **Email**: support@example.com

---

## Acknowledgments

- IEC standards for solar PV testing and certification
- OpenAI for GPT-4 language model
- Streamlit team for the amazing framework
- Solar PV community for domain expertise

---

## Roadmap

### Planned Features
- [ ] Real-time collaboration
- [ ] Multi-language support
- [ ] Custom training on proprietary documents
- [ ] Mobile app versions
- [ ] Integration with testing equipment
- [ ] Advanced analytics and reporting
- [ ] User authentication and profiles
- [ ] Team workspaces

---

## Version History

### v1.0.0 (Current)
- Initial release
- AI chat with RAG and citations
- Advanced search functionality
- 5 professional calculators
- Image analysis with defect detection
- Standards library
- Analytics dashboard
- Responsive design
- Comprehensive documentation

---

**Built with ❤️ for the Solar PV community**
