import csv
from pathlib import Path
import requests
from datetime import datetime

API_URL = "https://yc-oss.github.io/api/companies/all.json"
CSV_PATH = Path("yc_companies_master.csv")


def fetch_yc_companies():
    resp = requests.get(API_URL, timeout=60)
    resp.raise_for_status()
    return resp.json()


def load_existing_ids():
    if not CSV_PATH.exists():
        return set()
    ids = set()
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id"):
                ids.add(row["id"])
    return ids


def unix_to_date(ts):
    if ts is None:
        return ""
    try:
        return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
    except Exception:
        return ""


def append_new_companies(companies, existing_ids):
    fieldnames = [
        "id",
        "name",
        "slug",
        "website",
        "batch",
        "stage",
        "status",
        "industry",
        "subindustry",
        "all_locations",
        "team_size",
        "launched_at_date",
        "one_liner",
        "url",
        "api",
        "tags",
        "regions",
        "industries",
    ]

    file_exists = CSV_PATH.exists()

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        # If file didn't exist, write header first
        if not file_exists:
            writer.writeheader()

        new_count = 0
        for c in companies:
            cid = str(c.get("id"))
            if cid in existing_ids:
                continue

            row = {
                "id": cid,
                "name": c.get("name"),
                "slug": c.get("slug"),
                "website": c.get("website"),
                "batch": c.get("batch"),
                "stage": c.get("stage"),
                "status": c.get("status"),
                "industry": c.get("industry"),
                "subindustry": c.get("subindustry"),
                "all_locations": c.get("all_locations"),
                "team_size": c.get("team_size"),
                "launched_at_date": unix_to_date(c.get("launched_at")),
                "one_liner": c.get("one_liner"),
                "url": c.get("url"),
                "api": c.get("api"),
                "tags": ", ".join(c.get("tags", []) or []),
                "regions": ", ".join(c.get("regions", []) or []),
                "industries": ", ".join(c.get("industries", []) or []),
            }
            writer.writerow(row)
            new_count += 1

    print(f"Appended {new_count} new companies.")


def main():
    companies = fetch_yc_companies()

    # Optional: only keep Series A
    # companies = [c for c in companies if (c.get("stage") or "").lower() == "series a"]

    existing_ids = load_existing_ids()
    append_new_companies(companies, existing_ids)


if __name__ == "__main__":
    main()
