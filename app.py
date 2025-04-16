import streamlit as st
import os
import json
from dotenv import load_dotenv
from llm.claude_coder import ClaudeCoder
from utils.parser import clean_response, split_compound_response

# Load environment variables
load_dotenv()

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

try:
    # Get API key from Streamlit secrets or .env file
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables or Streamlit secrets")
    
    # Get other settings from Streamlit secrets or .env file
    model_name = st.secrets.get("MODEL_NAME") or os.getenv("MODEL_NAME", "claude-3-opus-20240229")
    max_tokens = int(st.secrets.get("MAX_TOKENS") or os.getenv("MAX_TOKENS", 4000))
    temperature = float(st.secrets.get("TEMPERATURE") or os.getenv("TEMPERATURE", 0.7))
    
    # Initialize Claude Coder
    coder = ClaudeCoder(
        api_key=api_key,
        model_name=model_name,
        max_tokens=max_tokens,
        temperature=temperature
    )
except Exception as e:
    st.error(f"Failed to initialize the coding system: {str(e)}")
    st.stop()

# Load codeframe
def load_codeframe():
    try:
        with open("data/codeframe.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load codeframe: {str(e)}")
        st.stop()

# Streamlit UI setup with mobile and dark mode support
st.set_page_config(
    page_title="AI Consultation Coder",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load external CSS
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Main title with responsive design
st.markdown("""
    <div class="app-title">
        <h1>📋 AI Consultation Coder</h1>
        <p class="app-subtitle">Automated coding of consultation responses using AI</p>
    </div>
""", unsafe_allow_html=True)

# Load codeframe for reference
codeframe = load_codeframe()

# Sidebar for configuration with mobile-friendly design
with st.sidebar:
    st.markdown("""
        <div class="section-header">
            <h2>Codeframe Reference</h2>
            <p class="app-subtitle">Search and browse available codes</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Search box for codes with improved styling
    search_term = st.text_input(
        "Search codes",
        "",
        placeholder="Type to search codes...",
        key="search_input"
    ).strip().lower()
    
    # Display codeframe with search filtering
    for category, codes in codeframe["categories"].items():
        # Check if any codes in this category match the search term
        matching_codes = {
            code: desc for code, desc in codes.items()
            if not search_term or 
            search_term in code.lower() or 
            search_term in desc.lower()
        }
        
        if matching_codes:  # Only show category if it has matching codes
            with st.expander(category.replace("_", " ").title()):
                for code, description in matching_codes.items():
                    st.markdown(f"""
                        <div class="code-reference">
                            <strong>{code}</strong>: {description}
                        </div>
                    """, unsafe_allow_html=True)

# Main content with responsive tabs
tab1, tab2 = st.tabs(["Single Response", "Batch Processing"])

with tab1:
    st.markdown("""
        <div class="section-header">
            <h2>Code a Single Response</h2>
            <p class="app-subtitle">Enter a question and response to get automated coding</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Input fields with improved styling
    question = st.text_input(
        "Question:",
        placeholder="Enter the consultation question...",
        key="question_input"
    )
    
    response = st.text_area(
        "Response:",
        height=200,
        placeholder="Enter the stakeholder's response...",
        key="response_input"
    )
    
    # Check if question has changed
    if question != st.session_state.current_question:
        st.session_state.current_question = question
        st.session_state.analysis_results = None
    
    if st.button("Analyze Response", key="analyze_button"):
        if not question or not response:
            st.warning("Please enter both a question and response!")
        else:
            with st.spinner("Analyzing response..."):
                try:
                    # Clean and process response
                    cleaned_response = clean_response(response)
                    statements = split_compound_response(cleaned_response)
                    
                    # Get coding from Claude
                    coding = coder.code_response(
                        response=cleaned_response,
                        question=question
                    )
                    
                    # Store results in session state
                    st.session_state.analysis_results = {
                        "cleaned_response": cleaned_response,
                        "statements": statements,
                        "coding": coding
                    }
                    
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
    
    # Display results if available
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        st.markdown("""
            <div class="section-header">
                <h2>Analysis Results</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Show cleaned response
        with st.expander("Cleaned Response"):
            st.write(results["cleaned_response"])
            st.markdown("**Individual Statements:**")
            for i, statement in enumerate(results["statements"], 1):
                st.markdown(f"{i}. {statement}")
        
        # Show assigned codes with descriptions
        coding = results["coding"]
        if "codes" in coding and coding["codes"]:
            st.success("Analysis complete!")
            
            # Display codes and their details
            st.markdown("### Assigned Codes")
            
            # Create columns for better layout
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown("**Code**")
                for code in coding["codes"]:
                    st.markdown(f"`{code}`")
            
            with col2:
                st.markdown("**Description & Analysis**")
                for code in coding["codes"]:
                    # Find code description
                    code_description = None
                    for category in codeframe["categories"].values():
                        if code in category:
                            code_description = category[code]
                            break
                    
                    # Display code description and analysis
                    st.markdown(f"**{code_description}**")
                    
                    # Confidence score
                    if "confidence" in coding and code in coding["confidence"]:
                        confidence = coding["confidence"][code]
                        st.progress(confidence, text=f"Confidence: {confidence:.2f}")
                    
                    # Explanation
                    if "explanation" in coding and code in coding["explanation"]:
                        st.markdown(coding["explanation"][code])
                    
                    # Relevant quote
                    if "relevant_quotes" in coding and code in coding["relevant_quotes"]:
                        st.markdown(f"> {coding['relevant_quotes'][code]}")
                    
                    st.markdown("---")
        else:
            st.warning("No codes were assigned to this response.")
            if "error" in coding:
                st.error(f"Error: {coding['error']}")

with tab2:
    st.markdown("""
        <div class="section-header">
            <h2>Batch Process Responses</h2>
            <p class="app-subtitle">Upload a CSV file to process multiple responses</p>
        </div>
    """, unsafe_allow_html=True)
    
    # File upload with improved styling
    uploaded_file = st.file_uploader(
        "Upload CSV file with responses",
        type=["csv"],
        help="CSV should have columns: 'question' and 'response'"
    )
    
    if uploaded_file:
        st.info("Batch processing coming soon!")
        
        if st.button("Process Batch", key="batch_button"):
            st.warning("Batch processing is not yet implemented")

# Footer with responsive design
st.markdown("""
    <div class="footer">
        <p>Made with ❤️ using Claude 3</p>
    </div>
""", unsafe_allow_html=True)
