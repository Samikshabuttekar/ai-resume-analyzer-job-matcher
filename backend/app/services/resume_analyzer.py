import re


KNOWN_SKILLS = [
    "Python",
    "Java",
    "SQL",
    "MySQL",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Streamlit",
    "NLP",
    "GitHub",
    "VS Code",
    "API Integration",
    "Data Structures & Algorithms",
    "DBMS",
    "Object-Oriented Programming",
]


def extract_email(text: str) -> str | None:
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
    )

    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text,
    )

    return match.group(0) if match else None


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()

    found_skills = []

    for skill in KNOWN_SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills


def analyze_resume(text: str) -> dict:
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
    }