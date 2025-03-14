import streamlit as st
from pathlib import Path
import base64

# Get the path to the assets directory
assets_path = Path(__file__).parent / "assets"

# Page config
st.set_page_config(
    page_title="Mark2Docx CV Suite",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for branding
st.markdown("""
    <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Page styling */
        .stApp {
            background: linear-gradient(135deg, #000000 0%, #131416 100%);
        }
        
        /* Header styling */
        .header {
            text-align: center;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        
        .logo-header {
            max-width: 200px;
            margin: 0 auto 1.5rem auto;
            display: block;
        }
        
        .title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #64748b;
            max-width: 600px;
            margin: 0 auto 1.5rem auto;
        }
        
        /* Feature card styling */
        .feature-card {
            background: #131416;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        
        .feature-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 0.75rem;
        }
        
        .feature-description {
            color: #64748b;
            margin-bottom: 1rem;
            line-height: 1.5;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e2e8f0;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 0.5rem;
        }
        
        .logo-container img {
            height: 30px;
        }
        
        .logo-text {
            color: #64748b;
            font-size: 0.9rem;
        }
        
        /* Button styling */
        .btn {
            display: inline-block;
            background: #663fff;
            color: white !important;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            transition: background 0.2s;
        }
        
        .btn:hover {
            background: #663faa;
            color: white !important;
            text-decoration: none;
        }
        
        .btn-disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }
        
        .btn-disabled:hover {
            background: #94a3b8;
        }
    </style>
""", unsafe_allow_html=True)

# Try to load the logo image
try:
    with open(assets_path / 'mark2docx.png', 'rb') as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Mark2Docx Logo" class="logo-header">'
except Exception as e:
    logo_html = '<div style="height: 60px; text-align: center; font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem;">Mark2Docx</div>'

# Header
st.markdown(f"""
    <div class="header">
        {logo_html}
        <p class="subtitle">Transform your CV workflow with powerful tools for parsing, formatting, and generating professional consultant profiles.</p>
    </div>
""", unsafe_allow_html=True)

# Feature cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3 class="feature-title">CV to Markdown Converter</h3>
            <p class="feature-description">
                Convert your existing CV formats into clean, structured markdown. Perfect for AI parsing, 
                version control, and as input for other tools in the suite.
            </p>
            <a href="/CV_to_Markdown" target="_self" class="btn">Convert CV</a>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <h3 class="feature-title">Generate Consultant CV</h3>
            <p class="feature-description">
                Create beautiful, professionally formatted Word documents from your structured CV data. 
                Includes customizable templates and automatic formatting.
            </p>
            <a href="/CV_to_Docx_Template" target="_self" class="btn">Generate DOCX</a>
        </div>
    """, unsafe_allow_html=True)

# Coming soon feature
st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔄</div>
        <h3 class="feature-title">CV Analyzer</h3>
        <p class="feature-description">
            Get insights and suggestions to improve your CV. Analyze keyword density, 
            identify missing skills, and compare against job requirements.
        </p>
        <a class="btn btn-disabled">Coming Soon</a>
    </div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"""
    <div class="footer">
        <div class="logo-container">
            <img src="data:image/svg+xml;base64,{base64.b64encode(open(assets_path / 'es.svg', 'rb').read()).decode()}" alt="Logo"/>
            <span class="logo-text">Created by Erik Svahn - Frontwalker</span>
        </div>
    </div>
""", unsafe_allow_html=True)
