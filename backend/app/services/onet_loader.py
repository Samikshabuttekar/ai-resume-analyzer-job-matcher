"""
Utilities for loading software technologies from the O*NET dataset.
"""

import csv
from pathlib import Path


ONET_FILE = Path("data/onet/software_skills.csv")


def load_onet_technologies() -> list[dict]:
    """
    Load unique software technologies from O*NET.

    Returns:
        A list containing technology name and metadata.
    """

    if not ONET_FILE.exists():
        raise FileNotFoundError(
            f"O*NET software skills file not found: {ONET_FILE}"
        )

    technologies = {}

    with ONET_FILE.open(
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            technology = row["Workplace Example"].strip()

            if not technology:
                continue

            key = technology.lower()

            if key not in technologies:
                technologies[key] = {
                    "name": technology,
                    "hot": row["Hot Technology"].strip().upper() == "Y",
                    "in_demand": row["In Demand"].strip().upper() == "Y",
                }

    return list(technologies.values())