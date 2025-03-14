import streamlit as st
import tempfile
import os
from docx_generator import generate_docx_cv
from cv_parser import html_to_markdown
from parse_cv_to_dict import parse_cv_to_dict, extract_consultant_image_from_docx
from pathlib import Path
import base64

# Get path to logo assets (adjust path if needed)
assets_path = Path(__file__).parent.parent / "assets"

# Page config
st.set_page_config(
    page_title="CV Generator from Template",
    page_icon="📄",
    layout="centered"
)



# Custom CSS for branding
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .logo-container {
            position: fixed;
            bottom: 60px;
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
            margin-bottom: 100px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.title("📄 CV Generator from DOCX Template")
st.markdown("Upload a Momang CV (.docx), extract structured data, and generate a new clean consultant CV.")

uploaded_file = st.file_uploader("Choose a DOCX file", type="docx", help="Only .docx files are supported")

if uploaded_file:
    try:
        with st.spinner("Converting and generating your new CV..."):
            # Save temp DOCX
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
                temp_docx.write(uploaded_file.getvalue())
                docx_path = temp_docx.name

            # Convert to Markdown
            with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_md:
                html_to_markdown(docx_path, temp_md.name)
                markdown_path = temp_md.name

            # Show Markdown preview
            with open(markdown_path, "r", encoding="utf-8") as f:
                markdown_preview = f.read()

            st.markdown("### 🔍 Preview Parsed Markdown")
            with st.expander("Show Markdown Preview"):
                st.markdown(markdown_preview)

            # Parse to structured dict
            cv_data = parse_cv_to_dict(markdown_path)
            cv_data["image_path"] = extract_consultant_image_from_docx(docx_path)

              # 🔥 STEP: Auto-extract consultant image from original DOCX
            image_path = extract_consultant_image_from_docx(docx_path)
            if image_path:
                cv_data["image_path"] = image_path

            # Show parsed JSON structure
            st.markdown("### 📂 Parsed Data Preview")
            with st.expander("Show Parsed Dictionary"):
                st.json(cv_data)

            if cv_data["image_path"]:
                st.image(cv_data["image_path"], caption="Extracted Consultant Photo", width=150)
            # Generate DOCX
            template_path = "templates/cv_template.docx"
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name

            generate_docx_cv(cv_data, template_path, output_path)

            st.success("✅ New CV generated successfully!")
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Download Final DOCX",
                    data=f.read(),
                    file_name=f"{cv_data.get('consultant_name', 'Consultant_CV')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            # Clean up temp files
            os.unlink(docx_path)
            os.unlink(markdown_path)
            os.unlink(output_path)

    except Exception as e:
        st.error(f"❌ Error occurred during processing: {str(e)}")

# Instructions
st.markdown("""
---
### ℹ️ How it works:
1. Upload your Momang DOCX CV
2. It will be converted to Markdown
3. Parsed into a structured format
4. Injected into your new DOCX Template
5. Download your new consultant CV 🎯
""")

# Footer branding
st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/svg+xml;base64,{base64.b64encode(open(assets_path / 'es.svg', 'rb').read()).decode()}" alt="Logo"/>
        <span class="logo-text">Created by Erik Svahn - Frontwalker</span>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
