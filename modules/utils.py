import streamlit as st

def setup_page():
    """
    Configure the Streamlit page settings
    """
    st.set_page_config(
        page_title="Stock Technical Analysis",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stButton>button {
            width: 100%;
        }
        .stProgress .st-bo {
            background-color: #FF4B4B;
        }
        </style>
    """, unsafe_allow_html=True)

## file_path: styles/custom.css
