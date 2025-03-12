import argparse
import subprocess
import os
from bs4 import BeautifulSoup, NavigableString, Tag
import re
import logging
import sys
import platform

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_environment():
    """Check environment details"""
    try:
        # Check Pandoc version
        result = subprocess.run(["pandoc", "--version"], 
                              capture_output=True, 
                              text=True)
        logger.debug(f"Pandoc version info:\n{result.stdout.split('\n')[0]}")
        
        # Check Python encoding
        logger.debug(f"Python file encoding: {sys.getdefaultencoding()}")
        
        # Check platform
        logger.debug(f"Platform: {platform.system()}")
    except Exception as e:
        logger.error(f"Error checking environment: {str(e)}")
        
def convert_docx_to_html(input_path: str) -> str:
    """First step: Convert DOCX to HTML using Pandoc"""
    check_environment()
    temp_html = "temp.html"
    try:
        result = subprocess.run([
            "pandoc",
            input_path,
            "-f", "docx",
            "-t", "html5",  # Specifically request HTML5 output
            "--wrap=none",  # Prevent line wrapping
            "--extract-media=.",  # Handle any embedded media
            "-s",  # Produce standalone document
            "--metadata", "pagetitle=CV",  # Add a title
            "-o", temp_html,
            "--verbose"
        ], check=True, capture_output=True, text=True)
        
        logger.debug(f"Pandoc stdout: {result.stdout}")
        logger.debug(f"Pandoc stderr: {result.stderr}")
        
        if not os.path.exists(temp_html):
            raise Exception("HTML file was not created")
            
        # Log the first few lines of the HTML file
        with open(temp_html, 'r', encoding='utf-8') as f:
            first_lines = ''.join(f.readlines()[:20])
            logger.debug(f"First few lines of HTML:\n{first_lines}")
            
        return temp_html
    except subprocess.CalledProcessError as e:
        raise Exception(f"Pandoc conversion failed: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error during conversion: {str(e)}")

def html_to_markdown(docx_path, output_path):
    """Convert DOCX to Markdown via HTML"""
    logger.debug(f"Starting conversion of {docx_path}")
    
    # First convert DOCX to HTML
    html_path = convert_docx_to_html(docx_path)
    logger.debug(f"HTML conversion complete: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        logger.debug(f"HTML content length: {len(html_content)}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        current_section = None
        
        for element in soup.find_all(['table', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if element.name == 'table':
                process_table(element, current_section)
            else:  # It's a heading
                heading_text = element.get_text(strip=True)
                current_section = heading_text
                level = int(element.name[1])
                markdown.append(f"{'#' * level} {heading_text}")
                markdown.append("")

    markdown = []
    current_section = None

    def handle_paragraph(element):
        """Handle paragraph elements, preserving <br /> as explicit line breaks."""
        text_parts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                text_parts.append(child.strip())
            elif child.name == 'br':
                text_parts.append('<br />')
            else:
                # Recursively process child elements
                text_parts.append(handle_paragraph(child))
        # Join text parts without adding spaces around <br />
        text = ''
        for part in text_parts:
            if part == '<br />':
                text += part
            else:
                if text and not text.endswith(' '):
                    text += ' '
                text += part
        # Replace multiple whitespaces with a single space
        text = ' '.join(text.split())
        return text

    def process_heading(element, level):
        """Process heading elements and append them to the Markdown list."""
        heading_text = element.get_text(separator=" ", strip=True)
        # Replace multiple whitespaces with a single space
        heading_text = ' '.join(heading_text.split())
        if heading_text:
            markdown.append(f"{'#' * level} {heading_text}")
            markdown.append("")  # Blank line after heading

    def process_cell_content(element):
        """Process the content within a table cell."""
        logger.debug(f"Processing element: {element.name if isinstance(element, Tag) else 'text'}")
        
        if isinstance(element, NavigableString):
            if not element.strip():
                return
            if element.parent.name == 'p':
                return
            text = element.strip()
            if text:
                # Check if this is a technology item (single word/phrase in a td)
                if (element.parent.name == 'td' and 
                    len(element.parent.get_text(strip=True).split()) <= 3 and
                    not any(word in text.lower() for word in ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']) and
                    not any(word in text for word in ['AB', 'Inc', 'LLC']) and  # Exclude company names
                    not text.endswith('er') and  # Exclude words like "Frontwalker"
                    not text.startswith('20')):  # Exclude years
                    logger.debug(f"Adding technology item: {text}")
                    markdown.append(f"- {text}")
                else:
                    logger.debug(f"Adding text: {text}")
                    markdown.append(text)
        elif isinstance(element, Tag):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                process_heading(element, level)
            elif element.name == 'p':
                para_text = handle_paragraph(element)
                if para_text:
                    markdown.append(para_text)
                    markdown.append('')
            elif element.name in ['ul', 'ol']:
                logger.debug(f"Processing list: {element.name}")
                list_items = element.find_all('li', recursive=False)
                logger.debug(f"Found {len(list_items)} list items")
                
                for index, li in enumerate(list_items, start=1):
                    li_text = li.get_text(separator=" ", strip=True)
                    li_text = ' '.join(li_text.split())
                    if li_text:
                        list_entry = f"- {li_text}" if element.name == 'ul' else f"{index}. {li_text}"
                        logger.debug(f"Adding list item: {list_entry}")
                        markdown.append(list_entry)
                markdown.append('')
            else:
                for child in element.contents:
                    process_cell_content(child)

    def process_table(table, current_section):
        """Process an HTML table and extract content into markdown."""
        technology_items = []  # Store technology items for this section
        
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            for cell in cells:
                # Process regular content
                for element in cell.contents:
                    if isinstance(element, NavigableString):
                        text = element.strip()
                        if text:
                            # Check if this is a technology item
                            if (len(text.split()) <= 3 and
                                not any(word in text.lower() for word in ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']) and
                                not any(word in text for word in ['AB', 'Inc', 'LLC']) and
                                not text.endswith('er') and
                                not text.startswith('20')):
                                technology_items.append(f"- {text}")
                                logger.debug(f"Adding technology item: {text}")
                            else:
                                markdown.append(text)
                    else:
                        process_cell_content(element)
        
        # Add technology items after the section content
        if technology_items:
            markdown.append("")  # Add blank line before technologies
            markdown.extend(technology_items)
            markdown.append("")  # Add blank line after technologies

    # Main document traversal
    root = soup.body or soup
    for element in root.find_all(recursive=False):
        if element.name == 'table':
            process_table(element, current_section)
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            heading_text = element.get_text(separator=" ", strip=True)
            # Replace multiple whitespaces with a single space
            heading_text = ' '.join(heading_text.split())
            current_section = heading_text  # Use the heading text directly
            process_heading(element, level)
        elif element.name == 'p':
            para_text = handle_paragraph(element)
            if para_text:
                para_text = ' '.join(para_text.split())
                markdown.append(para_text)
                markdown.append("")  # Blank line after paragraph
        else:
            # Process other elements if necessary
            pass

    # Clean up the markdown content
    markdown = clean_markdown(markdown)

    # Write the resulting Markdown to a file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(markdown))

    # Clean up temp file
    os.remove(html_path)

def main():
    parser = argparse.ArgumentParser(description='Convert DOCX to Markdown.')
    parser.add_argument('-i', '--input', required=True, help='Input DOCX file path')
    parser.add_argument('-o', '--output', required=True, help='Output Markdown file path')
    args = parser.parse_args()

    html_to_markdown(args.input, args.output)

if __name__ == '__main__':
    main()