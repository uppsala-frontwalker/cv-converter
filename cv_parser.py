import argparse
import subprocess
import os
from bs4 import BeautifulSoup, NavigableString, Tag
import re

def convert_docx_to_html(input_path: str) -> str:
    """First step: Convert DOCX to HTML using Pandoc"""
    temp_html = "temp.html"
    subprocess.run([
        "pandoc",
        input_path,
        "-f", "docx",
        "-t", "html",
        "-o", temp_html
    ])
    return temp_html

def html_to_markdown(docx_path, output_path):
    """Convert DOCX to Markdown via HTML"""
    # First convert DOCX to HTML
    html_path = convert_docx_to_html(docx_path)
    
    # Then process the HTML
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

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
        if isinstance(element, NavigableString):
            # Skip text nodes that are only whitespace
            if not element.strip():
                return
            # Check if parent is a paragraph
            if element.parent.name == 'p':
                # We will process this text within the paragraph handling
                return
            else:
                text = element.strip()
                if text:
                    markdown.append(text)
        elif isinstance(element, Tag):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                process_heading(element, level)
                # Already adds blank line
            elif element.name == 'p':
                para_text = handle_paragraph(element)
                if para_text:
                    markdown.append(para_text)
                    markdown.append('')  # Add blank line after paragraph
            elif element.name in ['ul', 'ol']:
                # Handle lists
                list_items = element.find_all('li', recursive=False)
                for index, li in enumerate(list_items, start=1):
                    li_text = li.get_text(separator=" ", strip=True)
                    li_text = ' '.join(li_text.split())
                    if element.name == 'ul':
                        markdown.append(f"- {li_text}")
                    else:
                        markdown.append(f"{index}. {li_text}")
                markdown.append('')  # Blank line after list
            else:
                # Recursively process other elements
                for child in element.contents:
                    process_cell_content(child)
        # No need to add a blank line here after cell content

    def process_table(table, current_section):
        """Process an HTML table and extract content into markdown."""
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) == 2:
                left_cell, right_cell = cells

                if current_section in ["Erfarenhet", "Experience"]:
                    # Left cell: company and date/location
                    # Process left cell
                    company_name = None
                    date_location = []
                    company = left_cell.find(['h5'])
                    if company:
                        company_name = company.get_text(separator=" ", strip=True)
                        company_name = ' '.join(company_name.split())
                    else:
                        company_name = handle_paragraph(left_cell)
                        company_name = ' '.join(company_name.split())

                    if company_name:
                        markdown.append(f"#### {company_name}")

                    # Process date and location
                    date_location_paras = left_cell.find_all('p')
                    for para in date_location_paras:
                        para_text = handle_paragraph(para)
                        para_text = ' '.join(para_text.split())
                        if '<br />' in para_text:
                            lines = para_text.split('<br />')
                            for line in lines:
                                line = line.strip()
                                if line:
                                    markdown.append(line)
                        else:
                            markdown.append(para_text)

                    markdown.append("")  # Blank line after company info

                    # Right cell: position and description
                    position = right_cell.find(['h5'])
                    if position:
                        position_title = position.get_text(separator=" ", strip=True)
                        position_title = ' '.join(position_title.split())
                        markdown.append(f"##### {position_title}")
                        markdown.append("")  # Blank line after position title

                    # Extract all text content from right cell for analysis
                    all_text_elements = []
                    
                    # Process paragraphs first (main description)
                    paragraphs = right_cell.find_all('p')
                    for para in paragraphs:
                        para_text = handle_paragraph(para)
                        if para_text:
                            para_text = ' '.join(para_text.split())
                            all_text_elements.append((para_text, len(para_text), 'paragraph'))
                    
                    # Process lists (could be tech stack in some versions)
                    lists = right_cell.find_all(['ul', 'ol'])
                    for lst in lists:
                        items = lst.find_all('li')
                        for item in items:
                            item_text = item.get_text(strip=True)
                            if item_text:
                                all_text_elements.append((item_text, len(item_text), 'list_item'))
                    
                    # Process spans and other inline elements (might be tech stack in some versions)
                    spans = right_cell.find_all(['span', 'strong', 'em', 'b', 'i'])
                    for span in spans:
                        # Only process if it's a direct child of the cell or within a div
                        # (to avoid processing spans inside paragraphs we already handled)
                        if span.parent.name in ['td', 'div']:
                            span_text = span.get_text(strip=True)
                            if span_text and len(span_text) < 50:  # Likely a tech stack item
                                all_text_elements.append((span_text, len(span_text), 'span'))
                    
                    # Process any remaining text nodes directly in the cell
                    for child in right_cell.children:
                        if isinstance(child, NavigableString) and child.strip():
                            text = child.strip()
                            if len(text) < 50:  # Likely a tech stack item
                                all_text_elements.append((text, len(text), 'text'))
                    
                    # Sort elements: longer paragraphs first (descriptions), then shorter items (tech stack)
                    all_text_elements.sort(key=lambda x: (-x[1], x[2]))
                    
                    # Add elements to markdown
                    description_added = False
                    tech_stack_items = []
                    
                    for text, length, elem_type in all_text_elements:
                        # Skip empty or very short items
                        if not text or len(text) < 2:
                            continue
                            
                        # Longer texts are likely descriptions
                        if length > 50 and not description_added:
                            markdown.append(text)
                            markdown.append("")  # Blank line after paragraph
                            description_added = True
                        # Shorter texts are likely tech stack items
                        elif length <= 50 and text not in tech_stack_items:
                            tech_stack_items.append(text)
                    
                    # Add tech stack items at the end
                    for item in tech_stack_items:
                        markdown.append(item)
                    
                    markdown.append("")  # Blank line after section

                elif current_section in ["Utbildning", "Education", "Kurser och certifieringar", "Courses and certifications", "Kompetenser", "Competences"]:
                    # Left cell: education info
                    # Right cell: date
                    paragraphs = left_cell.find_all('p')
                    if paragraphs:
                        for idx, para in enumerate(paragraphs):
                            para_text = handle_paragraph(para)
                            if idx == 0:
                                # For the first paragraph, handle <br /> within the heading
                                if '<br />' in para_text:
                                    heading_line, rest = para_text.split('<br />', 1)
                                    heading_line = ' '.join(heading_line.split())
                                    markdown.append(f"#### {heading_line}<br />")
                                    markdown.append('')  # Blank line after heading
                                    if rest.strip():
                                        rest = ' '.join(rest.strip().split())
                                        markdown.append(rest)
                                        markdown.append('')  # Blank line after paragraph
                                else:
                                    heading_line = ' '.join(para_text.strip().split())
                                    markdown.append(f"#### {heading_line}")
                                    markdown.append('')  # Blank line after heading
                            else:
                                if para_text:
                                    para_text = ' '.join(para_text.split())
                                    markdown.append(para_text)
                                    markdown.append('')  # Add blank line after paragraph
                    else:
                        # If there are no <p> elements, process the left cell as before
                        cell_text = handle_paragraph(left_cell)
                        if cell_text:
                            # Split the text at '<br />' to get lines
                            lines = cell_text.split('<br />')
                            if lines:
                                # The first line is the heading
                                heading_line = lines[0].strip()
                                heading_line = ' '.join(heading_line.split())
                                if '<br />' in cell_text:
                                    # Append '<br />' to the heading line to preserve it
                                    markdown.append(f"#### {heading_line}<br />")
                                    markdown.append('')  # Blank line after heading
                                else:
                                    markdown.append(f"#### {heading_line}")
                                    markdown.append('')  # Blank line after heading
                                # Remaining lines are additional info
                                for line in lines[1:]:
                                    line = line.strip()
                                    if line:
                                        line = ' '.join(line.split())
                                        markdown.append(line)
                                        markdown.append('')  # Blank line after line
                    # Append date
                    date = handle_paragraph(right_cell)
                    if date:
                        date = ' '.join(date.split())
                        markdown.append(date)
                    markdown.append("")  # Blank line after education entry

                elif current_section == "Språk":
                    # Left cell: language
                    # Right cell: proficiency level
                    language = handle_paragraph(left_cell)
                    proficiency = handle_paragraph(right_cell)
                    if language:
                        markdown.append(f"#### {language}")
                    if proficiency:
                        markdown.append(proficiency)
                    markdown.append("")  # Blank line after language entry

                else:
                    # Default processing for other sections
                    process_cell_content(left_cell)
                    process_cell_content(right_cell)
                    markdown.append("")  # Blank line after row
            else:
                # Handle rows with different number of cells if needed
                for cell in cells:
                    process_cell_content(cell)
                markdown.append("")  # Blank line after row

    def clean_markdown(markdown_lines):
        """Clean up the Markdown content by removing extra spaces."""
        cleaned_lines = []
        for line in markdown_lines:
            # Replace multiple spaces with a single space
            line = re.sub(r' {2,}', ' ', line)
            # Remove leading and trailing spaces
            line = line.strip()
            cleaned_lines.append(line)
        return cleaned_lines

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