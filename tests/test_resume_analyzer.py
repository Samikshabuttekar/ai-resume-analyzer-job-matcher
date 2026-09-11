from backend.app.services.resume_analyzer import (
    extract_experience,
    extract_name,
    extract_email,
    extract_phone,
)
from backend.app.services.resume_sections import detect_sections


def test_experience_with_present():
    text = """
EXPERIENCE

Software Developer | ABC Technologies | Hyderabad
January 2025 — Present
- Developed web applications using Python and FastAPI.
- Worked with REST APIs and MySQL.
"""

    sections = detect_sections(text)
    experience = extract_experience(text, sections)

    assert len(experience) == 1

    assert experience[0]["job_title"] == "Software Developer"
    assert experience[0]["company"] == "ABC Technologies"
    assert experience[0]["location"] == "Hyderabad"
    assert experience[0]["start_date"] == "January 2025"
    assert experience[0]["end_date"] == "Present"

    assert (
        "Developed web applications using Python and FastAPI."
        in experience[0]["description"]
    )

    assert (
        "Worked with REST APIs and MySQL."
        in experience[0]["description"]
    )


def test_experience_with_year_only_dates():
    text = """
EXPERIENCE

Backend Developer | XYZ Solutions
2024 - 2026
- Built REST APIs using Python and FastAPI.
- Worked with SQL databases.
"""

    sections = detect_sections(text)
    experience = extract_experience(text, sections)

    assert len(experience) == 1

    assert experience[0]["job_title"] == "Backend Developer"
    assert experience[0]["company"] == "XYZ Solutions"
    assert experience[0]["location"] is None
    assert experience[0]["start_date"] == "2024"
    assert experience[0]["end_date"] == "2026"

    assert (
        "Built REST APIs using Python and FastAPI."
        in experience[0]["description"]
    )

    assert (
        "Worked with SQL databases."
        in experience[0]["description"]
    )


def test_experience_with_separate_job_details():
    text = """
EXPERIENCE

Software Engineer
ABC Technologies
Hyderabad
January 2025 - Present
- Developed backend services using Python.
- Designed and integrated REST APIs.
"""

    sections = detect_sections(text)
    experience = extract_experience(text, sections)

    assert len(experience) == 1

    assert experience[0]["job_title"] == "Software Engineer"
    assert experience[0]["company"] == "ABC Technologies"
    assert experience[0]["location"] == "Hyderabad"
    assert experience[0]["start_date"] == "January 2025"
    assert experience[0]["end_date"] == "Present"

    assert (
        "Developed backend services using Python."
        in experience[0]["description"]
    )

    assert (
        "Designed and integrated REST APIs."
        in experience[0]["description"]
    )


def test_multiple_experience_entries():
    text = """
EXPERIENCE

Software Developer | ABC Technologies | Hyderabad
January 2025 - Present
- Built APIs using Python and FastAPI.

Junior Developer | XYZ Solutions | Pune
January 2023 - December 2024
- Developed web applications using JavaScript.
"""

    sections = detect_sections(text)
    experience = extract_experience(text, sections)

    assert len(experience) == 2

    assert experience[0]["job_title"] == "Software Developer"
    assert experience[0]["company"] == "ABC Technologies"
    assert experience[0]["location"] == "Hyderabad"
    assert experience[0]["start_date"] == "January 2025"
    assert experience[0]["end_date"] == "Present"

    assert (
        "Built APIs using Python and FastAPI."
        in experience[0]["description"]
    )

    assert experience[1]["job_title"] == "Junior Developer"
    assert experience[1]["company"] == "XYZ Solutions"
    assert experience[1]["location"] == "Pune"
    assert experience[1]["start_date"] == "January 2023"
    assert experience[1]["end_date"] == "December 2024"

    assert (
        "Developed web applications using JavaScript."
        in experience[1]["description"]
    )


def test_experience_with_abbreviated_months():
    text = """
EXPERIENCE

Full Stack Developer | Tech Solutions | Hyderabad
Jan 2025 - Present
- Developed web applications using React and Python.
- Integrated REST APIs with frontend applications.
"""

    sections = detect_sections(text)
    experience = extract_experience(text, sections)

    assert len(experience) == 1

    assert experience[0]["job_title"] == "Full Stack Developer"
    assert experience[0]["company"] == "Tech Solutions"
    assert experience[0]["location"] == "Hyderabad"
    assert experience[0]["start_date"] == "Jan 2025"
    assert experience[0]["end_date"] == "Present"

    assert (
        "Developed web applications using React and Python."
        in experience[0]["description"]
    )

    assert (
        "Integrated REST APIs with frontend applications."
        in experience[0]["description"]
    )


def test_experience_with_numeric_month_dates():
    text = """
EXPERIENCE

Software Engineer | ABC Technologies | Hyderabad
01/2025 - Present
Developed backend services.
"""

    sections = detect_sections(text)
    experience = extract_experience(text, sections)

    assert len(experience) == 1

    assert experience[0]["start_date"] == "01/2025"
    assert experience[0]["end_date"] == "Present"
    assert experience[0]["job_title"] == "Software Engineer"
    assert experience[0]["company"] == "ABC Technologies"
    assert experience[0]["location"] == "Hyderabad"

    assert (
        "Developed backend services."
        in experience[0]["description"]
    )


def test_basic_resume_contact_details():
    text = """
SAMIKSHA BUTTEKAR
samikshabuttekar@gmail.com | +91 9325893057 | Hyderabad

PROFESSIONAL SUMMARY
Artificial Intelligence and Data Science graduate.
"""

    assert extract_name(text) == "SAMIKSHA BUTTEKAR"
    assert extract_email(text) == "samikshabuttekar@gmail.com"
    assert extract_phone(text) == "+91 9325893057"