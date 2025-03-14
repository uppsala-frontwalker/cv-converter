import re
import zipfile
import tempfile
import os


def parse_cv_to_dict(markdown_path: str) -> dict:
    with open(markdown_path, "r", encoding="utf-8") as f:
        content = f.read()

    cv_data = {
        "consultant_name": "",
        "title": "",
        "summary": "",
        "skills": [],
        "tech": [],
        "certifications": [],
        "industries": [],
        "assignments": [],
        "education": [],
        "languages": [],
        "image_path": None
    }

    lines = content.splitlines()
    current_section = None
    summary_lines = []
    assignment = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if line.startswith("# "):
            cv_data["consultant_name"] = line[2:].strip()
            i += 1
            continue

        if line.startswith("## "):
            cv_data["title"] = line[3:].strip()
            i += 1
            continue

        if line.startswith("### "):
            current_section = line[4:].strip().lower()
            i += 1
            continue

        if current_section == "erfarenhet" and line.startswith("#### "):
            if assignment:
                cv_data["assignments"].append(assignment)
            assignment = {
                "company": line[5:].strip(),
                "role": "",
                "duration": "",
                "location": "",
                "description": "",
                "tech_stack": []
            }
            i += 1
            if i < len(lines) and re.search(r"\d{4}", lines[i]):
                assignment["duration"] = lines[i].strip()
                i += 1
            if i < len(lines) and lines[i] and not lines[i].startswith("#####") and not re.search(r"^\d{4}", lines[i]):
                assignment["location"] = lines[i].strip()
                i += 1
            if i < len(lines) and lines[i].startswith("#####"):
                assignment["role"] = lines[i].replace("#####", "").strip()
                i += 1

            desc_lines = []
            while i < len(lines) and not lines[i].startswith("#### ") and not lines[i].startswith("### "):
                current = lines[i].strip()
                if not current:
                    i += 1
                    continue
                if current.startswith("#####") and not assignment["role"]:
                    assignment["role"] = current.replace("#####", "").strip()
                elif len(current.split()) <= 3 and not current.endswith("."):
                    assignment["tech_stack"].append(current)
                else:
                    desc_lines.append(current)
                i += 1
            assignment["description"] = " ".join(desc_lines).strip()
            continue

        if current_section == "utbildning":
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#### "):
                    degree = line[5:].strip().replace("<br />", "").strip()
                    institution = ""
                    duration = ""
                    description = ""
                    desc_lines = []
                    i += 1

                    while i < len(lines) and not lines[i].startswith("#### ") and not lines[i].startswith("### "):
                        current_line = lines[i].strip()
                        if not current_line:
                            i += 1
                            continue
                        if not institution:
                            institution = current_line
                        elif re.search(r"\d{4}", current_line):
                            duration = current_line
                        else:
                            desc_lines.append(current_line)
                        i += 1

                    if desc_lines:
                        description = " ".join(desc_lines)

                    cv_data["education"].append({
                        "degree": degree,
                        "institution": institution,
                        "duration": duration,
                        "description": description
                    })
                elif line.startswith("### "):
                    break
                else:
                    i += 1
            continue

        if current_section == "kurser och certifieringar":
            while i < len(lines):
                line = lines[i].strip()
                if not line or line.startswith("### "):
                    break
                if line.startswith("#### "):
                    title = line[5:].strip()
                    description = ""
                    year = ""
                    desc_lines = []
                    i += 1
                    while i < len(lines) and not lines[i].startswith("#### ") and not lines[i].startswith("### "):
                        if re.match(r"^\d{4}$", lines[i].strip()):
                            year = lines[i].strip()
                            i += 1
                            break
                        desc_lines.append(lines[i].strip())
                        i += 1
                    description = " ".join(desc_lines)
                    cv_data["certifications"].append({
                        "title": title,
                        "description": description,
                        "year": year
                    })
                else:
                    i += 1
            continue

        if current_section == "språk" and line.startswith("#### "):
            lang_entry = {"language": line[5:].strip(), "proficiency": ""}
            i += 1
            if i < len(lines):
                lang_entry["proficiency"] = lines[i].strip()
                cv_data["languages"].append(lang_entry)
            continue

        if current_section == "kompetenser":
            if "," in line:
                for skill in line.split(","):
                    skill = skill.strip()
                    if skill:
                        cv_data["skills"].append(skill)
            else:
                cv_data["skills"].append(line)
            i += 1
            continue

        if current_section is None:
            summary_lines.append(line)

        i += 1

    if assignment:
        cv_data["assignments"].append(assignment)

    cv_data["summary"] = "\n".join(summary_lines).strip()
    return cv_data


def extract_consultant_image_from_docx(docx_path):
    import zipfile
    import tempfile
    import os

    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        media_files = [f for f in zip_ref.namelist() if f.startswith("word/media/")]
        media_files = sorted(media_files, key=lambda f: zip_ref.getinfo(f).file_size, reverse=True)
        for img in media_files:
            if not img.lower().endswith(('.emf', '.svg')):
                image_ext = os.path.splitext(img)[-1]
                image_temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=image_ext).name
                with open(image_temp_path, 'wb') as f:
                    f.write(zip_ref.read(img))
                return image_temp_path
    return None
