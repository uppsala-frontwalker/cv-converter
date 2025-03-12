import streamlit as st
import tempfile
import os
from cv_parser import html_to_markdown
from pathlib import Path
import base64

# Get the path to the assets directory
assets_path = Path(__file__).parent / "assets"

# Page config
st.set_page_config(
    page_title="CV DOCX to Markdown Converter",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for branding
st.markdown("""
    <style>
        .logo-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            opacity: 0.7;
        }
        .logo-container img {
            height: 30px;
        }
        .logo-text {
            color: #666;
            font-size: 12px;
        }
        .main-content {
            margin-bottom: 60px; /* Space for the fixed branding */
        }
    </style>
""", unsafe_allow_html=True)

# Main content div
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Title and description
st.title("CV DOCX to Markdown Converter")
st.markdown("Upload your CV in DOCX format and get it converted to Markdown!")

# File uploader
uploaded_file = st.file_uploader("Choose a DOCX file", type="docx", help="Only .docx files are supported")

if uploaded_file:
    try:
        # Show processing message
        with st.spinner('Converting your CV...'):
            # Create temporary files for processing
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
                temp_docx.write(uploaded_file.getvalue())
                
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as temp_md:
                # Convert the file
                html_to_markdown(temp_docx.name, temp_md.name)
                
                # Read the markdown content
                with open(temp_md.name, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()

            # Clean up temporary files
            os.unlink(temp_docx.name)
            os.unlink(temp_md.name)

        # Show success message
        st.success('Conversion completed!')

        # Preview section
        with st.expander("Preview Markdown"):
            st.markdown(markdown_content)

        # Download button
        st.download_button(
            label="📥 Download Markdown File",
            data=markdown_content,
            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.md",
            mime='text/markdown',
        )

    except Exception as e:
        st.error(f'An error occurred during conversion: {str(e)}')
        st.error('Please make sure you uploaded a valid DOCX file.')

# Add some helpful information
st.markdown("---")
st.markdown("""
### How to use:
1. Click 'Browse files' or drag and drop your DOCX file
2. Wait for the conversion to complete
3. Preview the result (optional)
4. Click 'Download Markdown File'
""")

st.markdown('</div>', unsafe_allow_html=True)

# Branding footer
st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/svg+xml;base64,{base64.b64encode(open(assets_path / 'es.svg', 'rb').read()).decode()}" alt="Frontwalker Logo"/>
        <span class="logo-text">Created by Erik Svahn - Frontwalker</span>
    </div>
""", unsafe_allow_html=True) 