import re

from backend.app.services.resume_sections import detect_sections


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


def extract_name(text: str) -> str | None:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    ignored_titles = {
        "resume",
        "cv",
        "curriculum vitae",
        "curriculum-vitae",
    }

    for line in lines[:5]:
        if line.lower() not in ignored_titles:
            return line

    return None


def extract_skills(text: str, sections: dict) -> list[str]:
    skills_text = sections.get("skills", "")

    if not skills_text:
        return []

    skills = []

    for line in skills_text.splitlines():
        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"^[A-Za-z][A-Za-z /&-]{0,30}:\s*",
            "",
            line,
        )

        parts = re.split(
            r"[,;|•·]",
            line,
        )

        for part in parts:
            skill = part.strip(" -–—\t")

            if skill:
                skills.append(skill)

    unique_skills = []

    for skill in skills:
        if skill.lower() not in [
            item.lower()
            for item in unique_skills
        ]:
            unique_skills.append(skill)

    return unique_skills


def extract_education(text: str, sections: dict) -> list[dict]:
    education_text = sections.get("education", "")

    if not education_text:
        return []

    lines = [
        line.strip()
        for line in education_text.splitlines()
        if line.strip()
    ]

    education = []
    current_entry = None

    date_pattern = (
        r"\b(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}\b"
        r"|\b(?:19|20)\d{2}\b"
    )

    score_pattern = (
        r"\b\d+(?:\.\d+)?\s*(?:%|GPA|CGPA)"
    )

    degree_pattern = (
        r"\b(?:"
        r"Bachelor|"
        r"Master|"
        r"B\.?E\.?|"
        r"B\.?Tech|"
        r"M\.?Tech|"
        r"BCA|"
        r"MCA|"
        r"BBA|"
        r"MBA|"
        r"BSc|"
        r"MSc|"
        r"B\.?Sc|"
        r"M\.?Sc|"
        r"BE|"
        r"ME|"
        r"Diploma|"
        r"Higher Secondary|"
        r"Secondary School|"
        r"High School|"
        r"Intermediate"
        r")\b"
    )

    for line in lines:

        # ---------------------------------------------------------
        # Is this a new education entry?
        # ---------------------------------------------------------
        is_new_entry = bool(
            re.search(
                degree_pattern,
                line,
                re.IGNORECASE,
            )
        )

        if is_new_entry:

            # Save previous entry.
            if current_entry:
                education.append(current_entry)

            current_entry = {
                "degree": None,
                "field": None,
                "institution": None,
                "date": None,
                "score": None,
            }

            working_line = line

            # -----------------------------------------------------
            # Extract score
            # -----------------------------------------------------
            score_match = re.search(
                score_pattern,
                working_line,
                re.IGNORECASE,
            )

            if score_match:
                current_entry["score"] = (
                    score_match.group(0).strip()
                )

                working_line = (
                    working_line[:score_match.start()]
                    + working_line[score_match.end():]
                )

            # -----------------------------------------------------
            # Extract date
            # -----------------------------------------------------
            date_matches = list(
                re.finditer(
                    date_pattern,
                    working_line,
                    re.IGNORECASE,
                )
            )

            if date_matches:
                date_match = date_matches[-1]

                current_entry["date"] = (
                    date_match.group(0).strip()
                )

                working_line = (
                    working_line[:date_match.start()]
                    + working_line[date_match.end():]
                )

            # -----------------------------------------------------
            # Split the education line using "|"
            # -----------------------------------------------------
            parts = [
                part.strip()
                for part in working_line.split("|")
                if part.strip()
            ]

            # -----------------------------------------------------
            # FIRST PART = degree + optional field
            # -----------------------------------------------------
            if parts:

                degree_part = parts[0].strip()

                # Field exists ONLY when an explicit dash is
                # present between degree and field.
                field_match = re.match(
                    r"^(.*?)\s+[–—-]\s+(.+)$",
                    degree_part,
                )

                if field_match:

                    current_entry["degree"] = (
                        field_match.group(1).strip()
                    )

                    current_entry["field"] = (
                        field_match.group(2).strip()
                    )

                else:

                    current_entry["degree"] = (
                        degree_part.strip()
                    )

                    # IMPORTANT:
                    # HSC / SSC have no field.
                    current_entry["field"] = None

            # -----------------------------------------------------
            # Find institution
            # -----------------------------------------------------
            if len(parts) >= 2:

                institution = parts[1].strip()

                # Remove leading dash.
                institution = institution.strip(
                    "—–- "
                ).strip()

                if institution:
                    current_entry["institution"] = (
                        institution
                    )

            # -----------------------------------------------------
            # Handle format where institution comes after "—"
            #
            # Example:
            # Higher Secondary School | March 2022 —
            # Baba Saheb Deshmukh Parvekar Science and Art College
            # -----------------------------------------------------
            if current_entry["institution"] is None:

                institution_match = re.search(
                    r"—\s*(.+)$",
                    working_line,
                )

                if institution_match:

                    institution = (
                        institution_match.group(1)
                        .strip()
                        .strip("|")
                        .strip()
                    )

                    if institution:
                        current_entry["institution"] = (
                            institution
                        )

        else:

            # -----------------------------------------------------
            # Continuation line
            # -----------------------------------------------------
            if current_entry is None:
                continue

            working_line = line

            # -----------------------------------------------------
            # Extract score
            # -----------------------------------------------------
            score_match = re.search(
                score_pattern,
                working_line,
                re.IGNORECASE,
            )

            if (
                score_match
                and current_entry["score"] is None
            ):
                current_entry["score"] = (
                    score_match.group(0).strip()
                )

            working_line = re.sub(
                score_pattern,
                "",
                working_line,
                flags=re.IGNORECASE,
            )

            # Remove score labels.
            working_line = re.sub(
                r"\b(?:Percentage|Percent|Score|GPA|CGPA)"
                r"\s*:?\s*",
                "",
                working_line,
                flags=re.IGNORECASE,
            )

            # -----------------------------------------------------
            # Extract date
            # -----------------------------------------------------
            if current_entry["date"] is None:

                date_match = re.search(
                    date_pattern,
                    working_line,
                    re.IGNORECASE,
                )

                if date_match:

                    current_entry["date"] = (
                        date_match.group(0).strip()
                    )

                    working_line = (
                        working_line[:date_match.start()]
                        + working_line[date_match.end():]
                    )

            # -----------------------------------------------------
            # Clean line
            # -----------------------------------------------------
            working_line = working_line.strip(
                " |—–-"
            ).strip()

            if not working_line:
                continue

            # -----------------------------------------------------
            # Add continuation information to institution.
            # -----------------------------------------------------
            if current_entry["institution"]:

                current_entry["institution"] = (
                    current_entry["institution"]
                    + ", "
                    + working_line
                )

            else:

                current_entry["institution"] = (
                    working_line
                )

    # Save final entry.
    if current_entry:
        education.append(current_entry)

    return education
def extract_projects(text: str, sections: dict) -> list[dict]:
    projects_text = sections.get("projects", "")

    if not projects_text:
        return []

    lines = [
        line.strip()
        for line in projects_text.splitlines()
        if line.strip()
    ]

    projects = []
    current_project = None

    for line in lines:
        # ---------------------------------------------------------
        # Detect a new project
        # ---------------------------------------------------------
        if current_project is None:
            current_project = {
                "name": line,
                "technologies": [],
                "description": [],
            }
            continue

        # ---------------------------------------------------------
        # Extract technology / tech stack information
        # ---------------------------------------------------------
        tech_match = re.search(
            r"^(?:Tech\s*Stack|Technologies|Technology|Tools)\s*:\s*(.+)$",
            line,
            re.IGNORECASE,
        )

        if tech_match:
            technologies = tech_match.group(1)

            current_project["technologies"] = [
                technology.strip()
                for technology in re.split(
                    r",|;|\|",
                    technologies,
                )
                if technology.strip()
            ]

            continue

        # ---------------------------------------------------------
        # Remove bullet characters from description
        # ---------------------------------------------------------
        cleaned_line = re.sub(
            r"^[\s•·▪▫◦‣⁃\-–—]+",
            "",
            line,
        ).strip()

        if cleaned_line:
            current_project["description"].append(
                cleaned_line
            )

    # -------------------------------------------------------------
    # Save final project
    # -------------------------------------------------------------
    if current_project:
        projects.append(current_project)

    return projects
def extract_certifications(text: str, sections: dict) -> list[str]:
    certifications_text = sections.get("certifications", "")

    if not certifications_text:
        return []

    certifications = []

    for line in certifications_text.splitlines():
        cleaned_line = re.sub(
            r"^[\s•·▪▫◦‣⁃\-–—]+",
            "",
            line,
        ).strip()

        if cleaned_line:
            certifications.append(cleaned_line)

    return certifications
def extract_achievements(text: str, sections: dict) -> list[str]:
    achievements_text = sections.get("achievements", "")

    if not achievements_text:
        return []

    achievements = []

    for line in achievements_text.splitlines():
        cleaned_line = re.sub(
            r"^[\s•·▪▫◦‣⁃\-–—]+",
            "",
            line,
        ).strip()

        if cleaned_line:
            achievements.append(cleaned_line)

    return achievements

def extract_experience(text: str, sections: dict) -> list[dict]:
    experience_text = sections.get("experience", "")

    if not experience_text:
        return []

    lines = [
        line.strip()
        for line in experience_text.splitlines()
        if line.strip()
    ]

    experience = []
    current_entry = None
    pending_details = []

    date_pattern = (
    r"\b(?:"
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
    r")\s+\d{4}\b"
    r"|"
    r"\b(?:0[1-9]|1[0-2])/\d{4}\b"
    r"|"
    r"\b(?:19|20)\d{2}\b"
    r"|"
    r"\b(?:Present|Current)\b"
)

    def create_entry():
        return {
            "job_title": None,
            "company": None,
            "location": None,
            "start_date": None,
            "end_date": None,
            "description": [],
        }

    def parse_job_details(line, entry):
        parts = [
            part.strip()
            for part in line.split("|")
            if part.strip()
        ]

        if len(parts) >= 1:
            entry["job_title"] = parts[0]

        if len(parts) >= 2:
            entry["company"] = parts[1]

        if len(parts) >= 3:
            entry["location"] = parts[2]

    def apply_pending_details(entry):
        if not pending_details:
            return

        if len(pending_details) >= 1:
            entry["job_title"] = pending_details[0]

        if len(pending_details) >= 2:
            entry["company"] = pending_details[1]

        if len(pending_details) >= 3:
            entry["location"] = pending_details[2]

    for line in lines:
        date_matches = list(
            re.finditer(
                date_pattern,
                line,
                re.IGNORECASE,
            )
        )

        # --------------------------------------------------
        # Case 1:
        # Job details and dates are on the SAME line
        #
        # Software Developer | ABC | Hyderabad | June 2025 - August 2025
        # --------------------------------------------------
        if date_matches:
            if current_entry is not None and current_entry["start_date"] is not None:
                experience.append(current_entry)
                current_entry = create_entry()

            if current_entry is None:
                current_entry = create_entry()

            dates = [
                match.group(0).strip()
                for match in date_matches
            ]

            current_entry["start_date"] = dates[0]

            if len(dates) >= 2:
                current_entry["end_date"] = dates[1]

            working_line = line

            for match in reversed(date_matches):
                working_line = (
                    working_line[:match.start()]
                    + working_line[match.end():]
                )

            working_line = working_line.strip(
                " |—–-"
            ).strip()

            if working_line:
                if "|" in working_line:
                    parse_job_details(
                        working_line,
                        current_entry,
                    )
                else:
                    apply_pending_details(current_entry)

            else:
                apply_pending_details(current_entry)

            pending_details = []

            continue

        # --------------------------------------------------
        # Case 2:
        # A new job-details line appears after an existing
        # completed experience entry.
        # --------------------------------------------------
        if current_entry is not None and current_entry["start_date"] is not None:
            if "|" in line:
                experience.append(current_entry)

                current_entry = create_entry()

                parse_job_details(
                    line,
                    current_entry,
                )

                continue

        # --------------------------------------------------
        # Case 3:
        # Job details appear BEFORE the date line.
        #
        # Software Engineer
        # ABC Technologies
        # Hyderabad
        # January 2025 - Present
        # --------------------------------------------------
        if current_entry is None:
            current_entry = create_entry()

        if current_entry["start_date"] is None:
            if "|" in line:
                parse_job_details(
                    line,
                    current_entry,
                )
            else:
                pending_details.append(line)

            continue

        # --------------------------------------------------
        # Case 4:
        # Description / bullet point after the date line.
        # --------------------------------------------------
        cleaned_line = re.sub(
            r"^[\s\u2022\u00b7\u25aa\u25ab\u25e6\u2023\u2043\-\u2013\u2014]+",
            "",
            line,
        ).strip()

        if cleaned_line:
            current_entry["description"].append(
                cleaned_line
            )

    if current_entry is not None:
        if current_entry["start_date"] is not None:
            experience.append(current_entry)

    return experience     

def extract_contact_info(text: str) -> dict:
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
    }
def analyze_resume(text: str) -> dict:
    sections = detect_sections(text)

    contact_info = extract_contact_info(text)

    return {
    "contact": contact_info,
    "skills": extract_skills(text, sections),
    "education": extract_education(text, sections),
    "projects": extract_projects(text, sections),
    "experience": extract_experience(text, sections),
    "certifications": extract_certifications(text, sections),
    "achievements": extract_achievements(text, sections),
    "sections": sections,
}
