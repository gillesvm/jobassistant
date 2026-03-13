"""
seed_jobs.py — Seed script for the jobassistant DynamoDB job-tracker table.
Used for initial setup and testing, helps to get down the structure of the table

Usage:
    python seed_jobs.py                          # uses default AWS profile + eu-central-1
    python seed_jobs.py --table my-table-name    # override table name
    python seed_jobs.py --region us-east-1       # override region
    python seed_jobs.py --profile myprofile      # override AWS profile

Requirements:
    pip install boto3
"""

import argparse
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_TABLE = "jobassistant-prod-job-tracker"  # adjust to match your name_prefix
DEFAULT_REGION = "eu-central-1"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%d-%m-%YT%H:%M:%SZ")


def make_job(
        company: str,
        job_title: str,
        job_url: str,
        status: str = "new",
        *,
        include_s3_keys: bool = False,
) -> dict:
    """
    Build a single job item.

    item_type = "JOB#METADATA" for the primary metadata record.
    dedupe_key is a normalised slug so the scraper can avoid duplicates.
    S3 key fields are omitted by default (absent = not yet generated).
    """
    job_id = str(uuid.uuid4())
    ts = now_iso()

    slug = f"{company.lower().replace(' ', '-')}#{job_title.lower().replace(' ', '-')}"

    item = {
        # ── Primary key ──────────────────────────────────────────────────────
        "job_id": job_id,
        "item_type": "JOB#METADATA",

        # ── Deduplication ────────────────────────────────────────────────────
        "dedupe_key": slug,

        # ── Job details ──────────────────────────────────────────────────────
        "company": company,
        "job_title": job_title,
        "job_url": job_url,

        # ── Workflow state (also used by GSI) ────────────────────────────────
        "status": status,

        # ── Timestamps ───────────────────────────────────────────────────────
        "created_at": ts,
        "updated_at": ts,
    }

    # S3 keys — only add when files already exist; omit entirely otherwise
    if include_s3_keys:
        item["s3_key_description"] = f"jobs/{job_id}/description.txt"
        item["s3_key_match_analysis"] = f"jobs/{job_id}/match_analysis.txt"
        item["s3_key_resume"] = f"jobs/{job_id}/resume.pdf"
        item["s3_key_cover_letter"] = f"jobs/{job_id}/cover_letter.pdf"

    return item


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SEED_JOBS = [
    {
        "company": "Stripe",
        "job_title": "Senior Backend Engineer",
        "job_url": "https://stripe.com/jobs/listing/senior-backend-engineer/1234",
        "status": "new",
    },
    {
        "company": "Anthropic",
        "job_title": "ML Infrastructure Engineer",
        "job_url": "https://boards.greenhouse.io/anthropic/jobs/5678",
        "status": "in_progress",
    },
    {
        "company": "Vercel",
        "job_title": "Developer Advocate",
        "job_url": "https://vercel.com/careers/developer-advocate-91011",
        "status": "applied",
        "include_s3_keys": True,  # simulate a job where docs were already generated
    },
    {
        "company": "Supabase",
        "job_title": "Full Stack Engineer",
        "job_url": "https://supabase.com/careers/full-stack-engineer",
        "status": "rejected",
    },
    {
        "company": "Linear",
        "job_title": "Product Designer",
        "job_url": "https://linear.app/careers/product-designer",
        "status": "new",
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def seed(table_name: str, region: str, profile: str | None) -> None:
    session = boto3.Session(profile_name=profile, region_name=region)
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)

    print(f"Target table : {table_name}  ({region})\n")

    with table.batch_writer() as batch:
        for spec in SEED_JOBS:
            item = make_job(
                company=spec["company"],
                job_title=spec["job_title"],
                job_url=spec["job_url"],
                status=spec.get("status", "new"),
                include_s3_keys=spec.get("include_s3_keys", False),
            )
            batch.put_item(Item=item)
            print(
                f"  ✓  {item['company']:20s}  {item['job_title']:35s}  status={item['status']:12s}  id={item['job_id']}")

    print(f"\nSeeded {len(SEED_JOBS)} items.")

    # ── Quick read-back via GSI ──────────────────────────────────────────────
    print("\n── GSI read-back (status=new) ──────────────────────────────────────")
    resp = table.query(
        IndexName="status-created-at-index",
        KeyConditionExpression=Key("status").eq("new"),
    )
    for r in resp["Items"]:
        print(f"  {r['company']:20s}  {r['job_title']:35s}  created_at={r['created_at']}")

    print("\nAll done. Table structure looks good.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the jobassistant DynamoDB table.")
    parser.add_argument("--table", default=DEFAULT_TABLE, help="DynamoDB table name")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region")
    parser.add_argument("--profile", default=None, help="AWS CLI profile name")
    args = parser.parse_args()

    seed(args.table, args.region, args.profile)
