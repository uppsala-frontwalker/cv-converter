from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import os
from jinja2 import Environment
from utils import crop_image_to_circle


def skill_list_with_checkmarks(skills):
    return "✔ " + "\n✔ ".join(skills)

def certification_titles_only(certifications):
    return "✔ " + "\n✔ ".join([cert.get("title", "") for cert in certifications])

def generate_docx_cv(data, template_path, output_path):
    """
    Fill the consultant CV template with data.
    Expects a data dictionary with fields:
        consultant_name, title, summary, skills, tech, certifications,
        industries, assignments (list of dicts), education, languages,
        image_path (optional).
    The company logo should be static in the template.
    """
    doc = DocxTemplate(template_path)

    # Limit items shown in main sections
    max_skills = 10
    max_certifications = 5

    # Prepare context for template rendering
    context = {
        "consultant_name": data.get("consultant_name", ""),
        "title": data.get("title", ""),
        "summary": data.get("summary", ""),
        "skills": data.get("skills", [])[:max_skills],
        "skills_full": data.get("skills", []),
        "tech": data.get("tech", []),
        "certifications": data.get("certifications", [])[:max_certifications],
        "certifications_full": data.get("certifications", []),
        "industries": data.get("industries", []),
        "assignments": data.get("assignments", []),
        "education": [
            {
                "degree": edu.get("degree", ""),
                "institution": edu.get("institution", "-"),
                "duration": edu.get("duration", "-")
            }
            for edu in data.get("education", [])
        ],
        "languages": [
            {
                "language": lang.get("language", ""),
                "proficiency": lang.get("proficiency", "-")
            }
            for lang in data.get("languages", [])
        ]
    }

    # Optional consultant image injection
    if data.get("image_path") and os.path.exists(data["image_path"]):
        rounded_path = data["image_path"].replace(".jpg", "_rounded.png")
        crop_image_to_circle(data["image_path"], rounded_path)
        context["image_block"] = InlineImage(doc, rounded_path, width=Mm(55))
    else:
        context["image_block"] = ""

    # Setup Jinja2 environment and add filter
    env = Environment(
        extensions=['jinja2.ext.loopcontrols'],
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False
    )
    env.filters['skill_checklist'] = skill_list_with_checkmarks
    env.filters['certification_titles'] = certification_titles_only

    # Render and save the DOCX
    doc.render(context, jinja_env=env)
    doc.save(output_path)


# Example usage
if __name__ == "__main__":
    example_data = {
        "consultant_name": "Philip Boukaras",
        "title": "Senior Fullstack-utvecklare",
        "summary": "Philip är en driven utvecklare...",
        "skills": ["Systemutveckling", "Integration", "Cloud"],
        "tech": ["C#", "React", "Kubernetes"],
        "certifications": ["AWS Developer"],
        "industries": ["Fintech", "Telekom"],
        "assignments": [
            {
                "company": "Vattenfall",
                "role": "Systemutvecklare",
                "dates": "Jan 2020 – Dec 2023",
                "description": "Arbetade med CI/CD pipelines...",
                "tech_stack": "C#, .NET, Jenkins"
            }
        ],
        "education": [
            {"degree": "M.Sc. Computer Science", "institution": "KTH", "duration": "2015–2020"}
        ],
        "languages": [
            {"language": "Svenska", "proficiency": "Modersmål"},
            {"language": "Engelska", "proficiency": "Flytande"}
        ],
        "image_path": "path/to/image.jpg"
    }

    generate_docx_cv(example_data, "templates/cv_template.docx", "output_cv.docx")
