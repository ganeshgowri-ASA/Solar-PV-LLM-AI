# Quick Start Guide

Get up and running with Solar PV LLM AI System in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

### 1. Clone and Navigate
```bash
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure (Optional for Demo)
```bash
# Copy environment template
cp .env.example .env

# Edit .env to add your OpenAI API key (optional for demo mode)
# nano .env
```

> **Note**: The application runs with mock data for demo purposes. OpenAI API key is only needed for production AI features.

### 4. Run the Application
```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`

## First Steps

### Explore the Chat Interface
1. Click on **Chat** in the sidebar
2. Try a suggested question or ask your own
3. View AI responses with sources and citations

### Search Standards
1. Navigate to **Search**
2. Enter keywords like "thermal testing" or "IEC 61215"
3. Apply filters and view results

### Use Calculators
1. Go to **Calculators**
2. Select a calculator tab (Energy Yield, System Sizing, ROI, etc.)
3. Enter your parameters and see instant results

### Analyze Images
1. Visit **Image Analysis**
2. Upload a solar panel image
3. Get AI-powered defect detection results

### Browse Standards
1. Open **Standards Library**
2. Browse by category
3. View detailed standard information

### View Dashboard
1. Check out **Dashboard**
2. Monitor system health and usage statistics
3. View performance trends

## Tips

- Use **Ctrl+R** to refresh the page
- All pages support **keyboard navigation**
- Data is **automatically saved** in session
- **Export** features available on most pages

## Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Clear Cache
```bash
streamlit cache clear
```

## Next Steps

- Read the [full documentation](../README.md)
- Explore [configuration options](../config/settings.py)
- Check out [example queries](EXAMPLES.md)
- Customize for your needs

## Support

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues)
- 💬 [Discussions](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/discussions)

Enjoy using Solar PV LLM AI System! ☀️
