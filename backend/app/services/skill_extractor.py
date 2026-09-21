"""
Skill extraction utilities using the O*NET software technology catalog.
"""

import re
from functools import lru_cache

from backend.app.services.onet_loader import load_onet_technologies


# These are naming variations, not a technology database.
# They map common job-description terms to a canonical technology name.
SKILL_ALIASES = {
    "oracle java": "java",
    "sun microsystems java": "java",
    "google angular": "angular",
    "amazon web services aws software": "aws",
    "microsoft azure software": "azure",
    "apache kafka": "kafka",
}


def normalize_skill(skill: str) -> str:
    """
    Normalize a technology name.
    """

    normalized = " ".join(
        skill.strip().lower().split()
    )

    return SKILL_ALIASES.get(
        normalized,
        normalized,
    )


@lru_cache(maxsize=1)
def build_skill_catalog() -> dict[str, str]:
    """
    Build a searchable O*NET technology catalog.

    The dictionary maps O*NET technology names to
    canonical technology names.
    """

    technologies = load_onet_technologies()

    catalog = {}

    for technology in technologies:

        name = technology["name"]

        normalized_name = normalize_skill(name)

        if normalized_name:
            catalog[name.lower()] = normalized_name

    # Add common technology names that O*NET represents
    # using a longer name.
    catalog["java"] = "java"
    catalog["angular"] = "angular"
    catalog["aws"] = "aws"
    catalog["azure"] = "azure"
    catalog["kafka"] = "kafka"

    return catalog


def extract_skills_from_text(text: str) -> list[str]:
    """
    Extract software technologies from text using O*NET.

    Matching uses word boundaries so that:
        Java != JavaScript
        Git != digital
        AWS != unrelated words
    """

    text_lower = text.lower()

    catalog = build_skill_catalog()

    found_skills = []

    # Match longer technology names first.
    sorted_terms = sorted(
        catalog.keys(),
        key=len,
        reverse=True,
    )

    for term in sorted_terms:

        pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
        if re.search(pattern, text_lower):

            canonical_skill = catalog[term]

            if canonical_skill not in found_skills:
                found_skills.append(canonical_skill)

    return sorted(found_skills)

       