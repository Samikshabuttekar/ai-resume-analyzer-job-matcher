from backend.app.services.job_matcher import (
    normalize_skill,
    match_skills,
    calculate_final_match_score,
    extract_job_skills,
    match_resume_to_job,
)


def test_normalize_skill():
    assert normalize_skill("K8s") == "kubernetes"
    assert normalize_skill("Postgres") == "postgresql"
    assert normalize_skill("RESTful API") == "rest"


def test_match_skills():
    result = match_skills(
        ["Java", "Spring Boot", "SQL", "Docker"],
        ["Java", "Spring Boot", "Kubernetes", "Kafka"],
    )

    assert result["matched_skills"] == ["java", "spring boot"]
    assert result["missing_skills"] == ["kafka", "kubernetes"]
    assert result["required_skill_count"] == 4
    assert result["matched_skill_count"] == 2
    assert result["skill_match_percentage"] == 50.0


def test_calculate_final_match_score():
    result = calculate_final_match_score(0.7467, 50.0)

    assert result == 64.8


def test_extract_job_skills():
    job = (
        "We are looking for a Java developer with Spring Boot, "
        "Kafka, PostgreSQL and Kubernetes experience."
    )

    result = extract_job_skills(job)

    assert result == [
        "java",
        "kafka",
        "kubernetes",
        "postgresql",
        "spring boot",
    ]


def test_match_resume_to_job():
    result = match_resume_to_job(
        "Java Spring Boot REST API development",
        ["Java", "Spring Boot", "SQL", "Docker"],
        "We are looking for a Java developer with Spring Boot, Kafka, PostgreSQL and Kubernetes experience.",
    )

    assert result["matched_skills"] == ["java", "spring boot"]
    assert result["missing_skills"] == [
        "kafka",
        "kubernetes",
        "postgresql",
    ]
    assert result["skill_match_percentage"] == 40.0