# 🍧 Slushie CFO Assistant

An AI-powered CFO assistant designed specifically for family-run slushie businesses. This comprehensive tool helps you manage finances, find deals, analyze data, optimize inventory, and make informed business decisions.

## Features

### 📊 Dashboard
- Real-time business metrics
- Revenue and profit tracking
- Flavor performance analysis
- Interactive charts and visualizations

### 🔍 Deal Finder
- Find the best deals on supplies and ingredients
- AI-powered procurement recommendations
- Supplier ratings and reviews
- Budget optimization suggestions

### 📈 Data Analysis
- Upload CSV files or enter data manually
- Consumer pattern analysis
- Sales trend visualization
- AI-powered insights and recommendations

### 📦 Inventory Recommendations
- AI-powered inventory optimization
- Flavor demand analysis
- Cost-saving recommendations
- Optimal stock level suggestions

### 💰 Profit Calculator
- Gross and net profit calculations
- Margin analysis
- Cost breakdown visualization
- Financial health insights

### 💬 Chat Assistant
- AI-powered business advice
- Financial guidance
- Operational insights
- Quick action buttons for common queries

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/slushie-cfo-assistant.git
cd slushie-cfo-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
   - Create a `.streamlit/secrets.toml` file
   - Add your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```

4. Run the application:
```bash
streamlit run streamlit_app.py
```

## Usage

### Dashboard
- View key business metrics at a glance
- Monitor revenue trends and flavor performance
- Track profit margins and growth

### Deal Finder
- Select the category of supplies you need
- Browse available deals with ratings
- Use AI analysis for personalized recommendations

### Data Analysis
- Upload your sales data in CSV format
- Or enter data manually for quick analysis
- Generate interactive charts and AI insights

### Inventory Management
- Input your current inventory levels
- Get AI recommendations for optimal stock levels
- Identify cost-saving opportunities

### Profit Calculator
- Enter your revenue and cost data
- Calculate gross and net profits
- Get AI-powered financial insights

### Chat Assistant
- Ask questions about your business
- Get advice on finances, operations, and strategy
- Use quick action buttons for common queries

## File Structure

```
jackdupras/
├── streamlit_app.py          # Main application
├── requirements.txt          # Python dependencies
├── README.md               # Documentation
├── .gitignore              # Git ignore rules
└── .streamlit/
    └── secrets.toml        # API keys (not in git)
```

## Dependencies

- **streamlit**: Web application framework
- **openai**: OpenAI API integration
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive charts and visualizations
- **numpy**: Numerical computing

## Security

- API keys are stored in `.streamlit/secrets.toml` (not committed to git)
- Virtual environment (`venv/`) is excluded from version control
- No sensitive data is hardcoded in the application

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🍧 Built with Streamlit & OpenAI for slushie business success!**
