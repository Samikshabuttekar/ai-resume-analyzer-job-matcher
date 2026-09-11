import re


SECTION_ALIASES = {

    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "about me",
        "about",
        "objective",
        "career objective",
        "career profile",
        "personal profile",
        "professional overview",
        "overview",
    ],

    "profile": [
        "web development profile",
        "development profile",
        "developer profile",
        "web developer profile",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "core competencies",
        "competencies",
        "technologies",
        "technical expertise",
        "technical knowledge",
        "key skills",
        "key competencies",
        "areas of expertise",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "career history",
        "work background",
        "professional background",
        "internship experience",
        "internships",
    ],
    "education": [
        "education",
        "educational background",
        "academic background",
        "academic qualifications",
        "educational qualifications",
        "academic history",
        "education and qualifications",
    ],
    "projects": [
        "projects",
        "project",
        "academic projects",
        "academic project",
        "personal projects",
        "personal project",
        "project experience",
        "key projects",
        "selected projects",
    ],
    "certifications": [
        "certifications",
        "certification",
        "certificates",
        "certificate",
        "professional certifications",
        "professional certification",
        "licenses",
        "licenses and certifications",
        "licenses and certificates",
    ],
    "achievements": [
        "achievements",
        "achievement",
        "accomplishments",
        "accomplishment",
        "awards",
        "award",
        "honors",
        "honours",
    ],
    "languages": [
        "languages",
        "language skills",
        "spoken languages",
        "languages known",
    ],
    "publications": [
        "publications",
        "publication",
        "research publications",
        "papers",
        "research papers",
    ],
    "volunteering": [
        "volunteering",
        "volunteer experience",
        "volunteer work",
        "community involvement",
    ],
    "interests": [
        "interests",
        "hobbies",
        "hobbies and interests",
        "personal interests",
    ],
    "references": [
        "references",
        "professional references",
        "references available on request",
    ],
}


# Normalize aliases once instead of recalculating them for every line.
NORMALIZED_ALIASES = {
    section_name: {
        re.sub(
            r"\s+",
            " ",
            re.sub(r"[^a-z\s]", "", alias.strip().lower()),
        )
        for alias in aliases
    }
    for section_name, aliases in SECTION_ALIASES.items()
}


def normalize_heading(line: str) -> str:
    line = line.strip().lower()

    line = re.sub(
        r"^[\s:•·\-–—|]+",
        "",
        line,
    )

    line = re.sub(
        r"[\s:•·\-–—|]+$",
        "",
        line,
    )

    line = re.sub(
        r"[^a-z\s]",
        "",
        line,
    )

    line = re.sub(
        r"\s+",
        " ",
        line,
    )

    return line.strip()


def detect_section_name(line: str) -> str | None:
    """
    Try to identify which resume section a line represents.
    """

    normalized_line = normalize_heading(line)

    if not normalized_line:
        return None

    for section_name, aliases in NORMALIZED_ALIASES.items():
        if normalized_line in aliases:
            return section_name

    return None


def is_likely_heading(line: str) -> bool:
    """
    Detect an unknown section heading.

    This helps with resumes that use headings we haven't
    explicitly listed in SECTION_ALIASES.

    Example:
        "WEB DEVELOPMENT PROFILE"
        "CAREER HIGHLIGHTS"
        "PROFESSIONAL MEMBERSHIPS"
    """

    stripped = line.strip()

    if not stripped:
        return False

    # A heading is usually short.
    words = stripped.split()

    if len(words) > 6:
        return False

    # Avoid treating normal sentences as headings.
    if stripped.endswith("."):
        return False

    # Ignore lines containing obvious sentence punctuation.
    if any(character in stripped for character in [",", "?", "!"]):
        return False

    # Strong signal: mostly uppercase.
    letters = [character for character in stripped if character.isalpha()]

    if not letters:
        return False

    uppercase_count = sum(
        character.isupper()
        for character in letters
    )

    uppercase_ratio = uppercase_count / len(letters)

    return uppercase_ratio >= 0.75


def detect_sections(text: str) -> dict:
    """
    Detect and separate sections from resume text.

    Known headings are mapped to standard section names.
    Unknown uppercase headings are placed into 'other'.
    """

    lines = text.splitlines()

    sections = {}
    current_section = None

    for index, line in enumerate(lines):
        stripped_line = line.strip()

        if not stripped_line:
            continue

        detected_section = detect_section_name(stripped_line)

        # Known section heading.
        if detected_section:
            current_section = detected_section
            sections[current_section] = []
            continue

        # Unknown but likely section heading.
        if is_likely_heading(stripped_line):

            # Avoid treating the person's name at the top
            # of the resume as a section heading.
            if index < 3 and current_section is None:
                continue

            current_section = "other"

            if current_section not in sections:
                sections[current_section] = []

            continue

        # Normal content belonging to the current section.
        if current_section:
            sections[current_section].append(stripped_line)

    # Convert lists into clean strings.
    cleaned_sections = {}

    for section_name, section_lines in sections.items():
        cleaned_text = "\n".join(
            line
            for line in section_lines
            if line.strip()
        ).strip()

        if cleaned_text:
            cleaned_sections[section_name] = cleaned_text

    return cleaned_sections