import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post
import base64

st.set_page_config(
    page_title="LinkedIn Post Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def apply_pastel_theme():
    st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #a8d5ba;
        color: #2c3e50;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #87c3a0;
        color: #1a202c;
    }
    .stSelectbox>div>div {
    background-color: #f0f7ff;
    border: 1px solid #d1e3ff;
    border-radius: 5px;
    color: #2c3e50 !important;
    }

    .css-1d3z3hw, .css-1cpxqw2 {
        color: #2c3e50 !important;
    }

    .css-1wy0on6 {
        color: #2c3e50 !important;
    }
    .css-145kmo2 {
        border: 1px solid #d1e3ff;
        border-radius: 5px;
        background-color: #f0f7ff;
    }
    h2 {
        color: #5a7d9a;
    }
    .output-box {
        background-color: #e5f1ff;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #a8d5ba;
        color: #2c3e50;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

def create_header():
    header_html = """
    <div style="background-color:#c4dbe7; padding:15px; border-radius:10px; margin-bottom:20px; 
                text-align:center; border-bottom:5px solid #8bc19c;">
        <h1 style="color:#1a202c; font-weight:700;">LinkedIn Post Generator</h1>
        <p style="color:#2c5270; font-style:italic; font-weight:500;">Create engaging posts for your professional network</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def create_card(content, title=None):
    card_html = f"""
    <div style="background-color:#e5f1ff; padding:20px; border-radius:10px; 
                margin-top:10px; border-left:5px solid #a8d5ba;">
        {f'<h3 style="color:#5a7d9a; margin-bottom:10px;">{title}</h3>' if title else ''}
        <div style="color:#2c3e50; font-weight:500;">{content}</div>
    </div>
    """
    return card_html

def main():
    apply_pastel_theme()
    create_header()
    
    fs = FewShotPosts()
    tags = fs.get_tags()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p style="color:#2c5270; font-weight:600;">Select Topic</p>', unsafe_allow_html=True)
        selected_tag = st.selectbox("", options=tags, label_visibility="collapsed")
    
    with col2:
        st.markdown('<p style="color:#2c5270; font-weight:600;">Post Length</p>', unsafe_allow_html=True)
        length_options = ["Short", "Medium", "Long"]
        selected_length = st.selectbox("", options=length_options, label_visibility="collapsed")
    
    with col3:
        st.markdown('<p style="color:#2c5270; font-weight:600;">Language</p>', unsafe_allow_html=True)
        language_options = ["English", "Indonesia", "Mixed"]
        selected_language = st.selectbox("", options=language_options, label_visibility="collapsed")
    
    st.markdown("<hr style='border:1px solid #d1e3ff; margin:20px 0px;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        generate_button = st.button("✨ Generate Post", use_container_width=True)
    
    if generate_button:
        with st.spinner("Creating your professional post..."):
            post = generate_post(selected_length, selected_language, selected_tag)
        
        st.markdown("<h3 style='color:#2c5270; margin-top:20px; font-weight:600;'>Your Generated LinkedIn Post</h3>", 
                    unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="output-box">
            <span style="color: #2c3e50; font-weight: 500; font-size: 16px;">
                {post.replace("\n", "<br>")}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='display:flex; justify-content:flex-end; margin-top:10px;'>", 
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy to clipboard", use_container_width=True):
                st.success("Post copied to clipboard!")
            
        with col2:
            if st.button("🔄 Generate Another", use_container_width=True):
                st.experimental_rerun()

if __name__ == "__main__":
    main()