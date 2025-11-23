# Usage Examples

Real-world examples of using the Solar PV LLM AI System for various tasks.

## Chat Interface Examples

### Question 1: Understanding Standards
**User Query:**
> "What are the key requirements in IEC 61215 for thermal cycling tests?"

**Expected Response:**
- Detailed explanation of thermal cycling test procedures
- Temperature range specifications (-40°C to +85°C)
- Number of cycles required
- Pass/fail criteria
- Sources cited from IEC 61215 standard

### Question 2: Performance Calculations
**User Query:**
> "How do I calculate the performance ratio of my solar PV system?"

**Expected Response:**
- Formula for performance ratio
- Required measurements
- Typical values and benchmarks
- Factors affecting performance ratio
- Relevant citations

### Question 3: Defect Analysis
**User Query:**
> "What causes hot-spots in solar panels and how can they be detected?"

**Expected Response:**
- Explanation of hot-spot causes
- Detection methods (thermal imaging, I-V curves)
- Prevention strategies
- IEC standard references
- Safety implications

## Search Examples

### Example 1: Find Safety Standards
**Search Query:** "safety"
**Filters:**
- Category: Safety
- Difficulty: Intermediate

**Expected Results:**
- IEC 61730 - PV Module Safety Qualification
- IEC 62109 - Power Converters Safety
- Related safety standards

### Example 2: Module Testing Procedures
**Search Query:** "module testing"
**Filters:**
- Category: Module Testing
- Test Type: Environmental Testing

**Expected Results:**
- IEC 61215 - Design Qualification
- IEC 61853 - Performance Testing
- Detailed test procedures

## Calculator Examples

### Example 1: Energy Yield Calculation
**Input:**
- System Size: 10 kW
- Daily Irradiance: 5.5 kWh/m²/day
- Performance Ratio: 0.80

**Expected Output:**
- Daily Energy: 44.0 kWh
- Monthly Energy: 1,320 kWh
- Annual Energy: 15.84 MWh
- CO₂ Offset: 7,920 kg/year
- Monthly breakdown chart

### Example 2: System Sizing
**Input:**
- Daily Consumption: 30 kWh
- Peak Sun Hours: 5
- System Efficiency: 0.80

**Expected Output:**
- Required System: 7.5 kW
- Recommended Panels: 19 × 400W
- Total Capacity: 7.6 kW
- Roof Area: 38 m²
- System composition pie chart

### Example 3: ROI Calculation
**Input:**
- System Cost: $15,000
- Annual Savings: $2,000
- Electricity Rate Increase: 3%
- Incentives: $3,000

**Expected Output:**
- Payback Period: 6.0 years
- 25-Year ROI: 233%
- Total Savings: $52,340
- Net Profit: $40,340
- Cash flow chart

### Example 4: Efficiency Analysis
**Input:**
- Max Power: 400 W
- Module Area: 2.0 m²
- Irradiance: 1000 W/m²
- Temperature: 45°C

**Expected Output:**
- Module Efficiency: 20.00%
- Actual Efficiency: 18.40%
- Temperature Loss: -1.60%
- Power Density: 200 W/m²
- Temperature performance curve

### Example 5: Shading Analysis
**Input:**
- Unshaded Production: 7,500 kWh
- Morning Shading: 15%
- Midday Shading: 5%
- Evening Shading: 20%

**Expected Output:**
- Total Loss: 12.5%
- Actual Production: 6,563 kWh
- Energy Loss: 937 kWh
- Annual Value Loss: $112
- Shading distribution chart
- Recommendations based on severity

## Image Analysis Examples

### Example 1: Module Inspection
**Upload:** Image of crystalline silicon solar panel
**Analysis Type:** Comprehensive

**Expected Results:**
- Module Type: Monocrystalline Silicon
- Detected Defects:
  - Micro-crack in Cell A5 (Medium severity, 87% confidence)
  - Hot-spot in Cell B3 (Low severity, 72% confidence)
- Overall Health: Good
- Estimated Power Loss: 2.3%
- Recommendations:
  - Monitor micro-crack for degradation
  - Verify bypass diode functionality
  - Schedule follow-up in 6 months

### Example 2: Thermal Image Analysis
**Upload:** Thermal camera image of PV array
**Analysis Type:** Thermal Only

**Expected Results:**
- Hot-spot locations identified
- Temperature differential mapping
- Bypass diode health assessment
- Immediate action items

## Standards Library Examples

### Example 1: Explore IEC 61215
**Navigation:** Browse > Module Testing > IEC 61215

**View:**
- Full standard title and description
- 18 major sections listed
- Difficulty: Advanced
- Related standards: IEC 61730, IEC 61853
- Ask AI questions about specific sections

### Example 2: Quick Reference
**Scenario:** Need to understand grid connection requirements

**Action:**
1. Search for "grid connection"
2. Find IEC 62446 standard
3. View detailed sections
4. Download summary PDF
5. Ask AI specific questions

## Dashboard Examples

### Example 1: Monitor System Health
**View:** Dashboard > System Health

**Metrics Displayed:**
- System Status: 🟢 Healthy
- Uptime: 99.7%
- Active Queries: 23
- Avg Response: 287 ms

### Example 2: Usage Analytics
**View:** Dashboard > Performance Trends

**Charts Available:**
- 30-day query volume trend
- Response time over time
- Success rate tracking
- Category distribution

### Example 3: Export Reports
**Action:**
1. Navigate to Dashboard
2. Click "Export Metrics"
3. Download JSON with all data
4. Use for external reporting

## Multi-Device Compatibility

### Desktop (1920×1080)
- Full sidebar navigation
- Multi-column layouts
- Large charts and visualizations
- All features accessible

### Tablet (768×1024)
- Collapsible sidebar
- Responsive columns
- Touch-optimized controls
- Swipe navigation

### Mobile (375×667)
- Hamburger menu
- Single-column layout
- Simplified charts
- Touch-friendly buttons
- Optimized image uploads

## Accessibility Examples

### Keyboard Navigation
- Tab through all interactive elements
- Enter to activate buttons
- Arrow keys in dropdowns
- Escape to close modals

### Screen Reader Support
- Semantic HTML structure
- ARIA labels on all controls
- Alt text for images
- Descriptive link text

## Integration Examples

### Example 1: Export to Excel
```python
# From any page with data
1. Click "Export as CSV"
2. Open in Excel
3. Create pivot tables
4. Generate reports
```

### Example 2: API Integration (Future)
```python
import requests

# Query the API
response = requests.post(
    "https://api.solarpvai.com/chat",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={"message": "What is IEC 61215?"}
)

answer = response.json()["content"]
sources = response.json()["sources"]
```

## Best Practices

### For Research
1. Start with broad searches
2. Apply filters progressively
3. Export results for offline analysis
4. Use chat for clarifications

### For Design Work
1. Use calculators for initial sizing
2. Validate with standards library
3. Document decisions in chat
4. Export calculations for reports

### For Inspection
1. Upload high-quality images
2. Use comprehensive analysis
3. Download defect reports
4. Follow up with AI chat for details

### For Training
1. Explore standards library systematically
2. Use suggested questions
3. Compare related standards
4. Export summaries for study materials

## Common Workflows

### Workflow 1: New System Design
1. **Calculators** → System Sizing
2. **Calculators** → Energy Yield
3. **Calculators** → ROI Analysis
4. **Standards Library** → Review IEC 62446
5. **Chat** → Ask design questions
6. Export all results

### Workflow 2: Module Quality Assessment
1. **Image Analysis** → Upload module photos
2. Review defect report
3. **Chat** → Ask about defect implications
4. **Standards Library** → Check IEC 61215 requirements
5. Generate inspection report

### Workflow 3: Learning IEC Standards
1. **Standards Library** → Browse by category
2. Select difficulty level
3. Read detailed sections
4. **Chat** → Ask clarifying questions
5. Download summaries
6. Review related standards

## Tips for Best Results

### Chat Interface
- Be specific in questions
- Reference standard numbers when relevant
- Ask follow-up questions
- Export important conversations

### Search
- Use technical terms
- Combine filters
- Try different view modes
- Export results early

### Calculators
- Double-check input units
- Use realistic values
- Compare multiple scenarios
- Save charts as images

### Image Analysis
- Use high-resolution images
- Ensure good lighting
- Capture entire module
- Upload multiple angles if needed

---

For more examples and use cases, visit our [wiki](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/wiki) or join the discussions!
