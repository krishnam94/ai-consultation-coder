# 📋 AI Consultation Coder

An AI-powered tool for automatically coding consultation responses using Claude 3. This application helps analyze stakeholder feedback and assign relevant codes based on a predefined codeframe.

## 🔗 Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-consultation-coder.streamlit.app/)

Try out the live demo to see the AI Consultation Coder in action!

## ✨ Features

- **Single Response Analysis**: Analyze individual consultation responses with detailed coding
- **Batch Processing**: Process multiple responses from a CSV file (coming soon)
- **Mobile Responsive**: Works seamlessly on both desktop and mobile devices
- **Interactive Code Reference**: Searchable codeframe in the sidebar
- **Detailed Analysis**: Includes confidence scores, explanations, and relevant quotes

## 🚀 Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-consultation-coder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
ANTHROPIC_API_KEY=your_api_key_here
MODEL_NAME=claude-3-opus-20240229  # Optional
MAX_TOKENS=4000  # Optional
TEMPERATURE=0.7  # Optional
```

4. Run the application:
```bash
streamlit run app.py
```

## 📁 Project Structure

```
ai-consultation-coder/
├── app.py                 # Main Streamlit application
├── static/
│   └── styles.css        # Custom CSS styles
├── data/
│   ├── codeframe.json    # Codeframe definitions
│   └── sample_responses.csv  # Sample consultation responses
├── llm/
│   └── claude_coder.py   # Claude integration
├── utils/
│   └── parser.py         # Response parsing utilities
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables
```

## 💡 Usage

### Single Response Analysis

1. Enter the consultation question
2. Paste the stakeholder's response
3. Click "Analyze Response"
4. View the results including:
   - Cleaned response
   - Individual statements
   - Assigned codes with descriptions
   - Confidence scores
   - Explanations
   - Relevant quotes

### Batch Processing

1. Prepare a CSV file with columns:
   - `question`: The consultation question
   - `response`: The stakeholder's response
2. Upload the file in the "Batch Processing" tab
3. Click "Process Batch" to analyze all responses

### Code Reference

- Use the sidebar to search and browse available codes
- Codes are organized by categories
- Search works on both code numbers and descriptions

## 🔧 Technical Details

- **AI Model**: Claude 3 (configurable)
- **Response Processing**: 
  - Cleans and normalizes responses
  - Splits compound responses into individual statements
  - Assigns codes with confidence scores
- **UI Features**:
  - Responsive design for all screen sizes
  - Interactive code reference
  - Real-time analysis
  - Session state management

## 🛠️ Development

### Adding New Codes

1. Edit `data/codeframe.json`
2. Add new codes to the appropriate categories
3. The changes will be reflected in the sidebar immediately

### Customizing Styles

1. Edit `static/styles.css`
2. Modify the CSS to change the appearance
3. The changes will be applied automatically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Claude 3](https://www.anthropic.com/)
- Inspired by consultation analysis needs 