import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.services.skill_extractor import extract_skills_from_text


model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_semantic_similarity(
    resume_text: str,
    job_description: str,
) -> float:
    """
    Calculate semantic similarity between a resume
    and a job description.
    """

    resume_embedding = model.encode([resume_text])

    job_embedding = model.encode([job_description])

    similarity = cosine_similarity(
        resume_embedding,
        job_embedding,
    )[0][0]

    return round(float(similarity), 4)

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name.
    """

    normalized = " ".join(
        skill.strip().lower().split()
    )

    # Remove proficiency annotations such as:
    # JavaScript (Basic) -> JavaScript
    # React (Learning) -> React
    normalized = re.sub(
        r"\s*\([^)]*\)",
        "",
        normalized,
    ).strip()

    aliases = {
        "k8s": "kubernetes",
        "postgres": "postgresql",
        "springboot": "spring boot",
        "rest api": "rest",
        "restful api": "rest",
        "restful services": "rest",
        "rest services": "rest",
    }

    return aliases.get(
        normalized,
        normalized,
    )




    aliases = {
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "springboot": "spring boot",
    "rest api": "rest",
    "restful api": "rest",
    "restful services": "rest",
    "rest services": "rest",
}

    return aliases.get(
        normalized,
        normalized,
    )


def match_skills(
    resume_skills: list[str],
    job_skills: list[str],
) -> dict:
    """
    Compare resume skills with required job skills.
    """

    normalized_resume_skills = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    normalized_job_skills = {
        normalize_skill(skill)
        for skill in job_skills
    }

    matched_skills = sorted(
        normalized_resume_skills
        & normalized_job_skills
    )

    missing_skills = sorted(
        normalized_job_skills
        - normalized_resume_skills
    )

    skill_match_percentage = (
        len(matched_skills)
        / len(normalized_job_skills)
        * 100
        if normalized_job_skills
        else 0.0
    )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "required_skill_count": len(normalized_job_skills),
        "matched_skill_count": len(matched_skills),
        "skill_match_percentage": round(
            skill_match_percentage,
            2,
        ),
    }


def calculate_final_match_score(
    semantic_similarity: float,
    skill_match_percentage: float,
) -> float:
    """
    Calculate the final resume-job match score.

    Semantic similarity contributes 60%.
    Explicit skill matching contributes 40%.
    """

    semantic_score = semantic_similarity * 100

    final_score = (
        semantic_score * 0.60
        + skill_match_percentage * 0.40
    )

    return round(final_score, 2)


def extract_job_skills(
    job_description: str,
) -> list[str]:
    """
    Extract technologies from a job description
    using the O*NET-based skill extractor.
    """

    return extract_skills_from_text(
        job_description
    )


def match_resume_to_job(
    resume_text: str,
    resume_skills: list[str],
    job_description: str,
) -> dict:
    """
    Match a resume against a job description.
    """

    job_skills = extract_job_skills(
        job_description
    )

    semantic_similarity = calculate_semantic_similarity(
        resume_text,
        job_description,
    )

    skill_match = match_skills(
        resume_skills,
        job_skills,
    )

    final_score = calculate_final_match_score(
        semantic_similarity,
        skill_match["skill_match_percentage"],
    )

    return {
        "final_match_score": final_score,
        "semantic_similarity": round(
            semantic_similarity * 100,
            2,
        ),
        "skill_match_percentage": skill_match[
            "skill_match_percentage"
        ],
        "matched_skills": skill_match[
            "matched_skills"
        ],
        "missing_skills": skill_match[
            "missing_skills"
        ],
    }