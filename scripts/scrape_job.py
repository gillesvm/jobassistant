"""
scrape_job.py — Scrape a LinkedIn job posting and store it in S3 + DynamoDB.

Usage:
    python scripts/scrape_job.py --url "https://www.linkedin.com/jobs/view/1234567890"
    AWS_PROFILE=eddy python scripts/scrape_job.py --url "..."

Setup (first time):
    pip install playwright boto3 python-dotenv
    playwright install chromium

.env file (never commit this):
    LINKEDIN_EMAIL=your@email.com
    LINKEDIN_PASSWORD=yourpassword

Future Lambda migration:
    Replace _get_credentials() to read from AWS Secrets Manager instead of .env.
    Replace _scrape_with_playwright() body to call Apify API instead.
    Everything else (S3 upload, DynamoDB write) stays identical.

Requirements:
    pip install playwright boto3 python-dotenv
"""

import argparse
import os
import re
import time
import uuid
from datetime import datetime, timezone

import boto3
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_TABLE = "jobassistant-prod-job-tracker"  # adjust to your name_prefix
DEFAULT_REGION = "eu-west-1"
S3_BUCKET = "jobassistant-prod-job-artifacts"
S3_PREFIX = "jobdescriptions"

LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    """Return current Brussels time as ISO 8601 string."""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Europe/Brussels")
    return datetime.now(tz).strftime("%d-%m-%YT%H:%M:%SZ")


def _get_credentials() -> tuple[str, str]:
    """
    Load LinkedIn credentials.

    LOCAL:  reads LINKEDIN_EMAIL / LINKEDIN_PASSWORD from .env
    LAMBDA: swap this function body to read from AWS Secrets Manager:

        import json
        client = boto3.client("secretsmanager", region_name="eu-west-1")
        secret = json.loads(
            client.get_secret_value(SecretId="jobassistant/linkedin")["SecretString"]
        )
        return secret["email"], secret["password"]
    """
    load_dotenv()
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        raise ValueError(
            "LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in your .env file."
        )
    return email, password


def _extract_job_id_from_url(url: str) -> str | None:
    """Pull the numeric LinkedIn job ID out of the URL if present."""
    match = re.search(r"/jobs/view/(\d+)", url)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Scraping — swap this function for Apify/ScrapingBee when needed
# ---------------------------------------------------------------------------

def _scrape_with_playwright(job_url: str) -> dict:
    """
    Open a headless Chromium browser, log in to LinkedIn, navigate to the
    job posting, and extract company, title, and full description.

    Returns:
        {
            "company":     str,
            "job_title":   str,
            "description": str,   # full plain-text job description
        }

    TO MIGRATE TO APIFY:
        Replace this entire function body with an HTTP call to the Apify
        LinkedIn Jobs Scraper actor and map the response fields to the same
        return dict. Nothing outside this function needs to change.
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    email, password = _get_credentials()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        # ── Step 1: Log in ───────────────────────────────────────────────────
        print("  → Navigating to LinkedIn login…")
        page.goto(LINKEDIN_LOGIN_URL, wait_until="networkidle")
        page.fill("#username", email)
        page.fill("#password", password)
        page.click('[type="submit"]')

        try:
            # Wait for the feed or the nav — confirms successful login
            page.wait_for_selector(
                "a[href*='/feed/'], nav.global-nav",
                timeout=15_000,
            )
            print("  → Logged in successfully.")
        except PWTimeout:
            # LinkedIn may ask for a verification code — surface it clearly
            page.screenshot(path="/tmp/linkedin_login_failed.png")
            raise RuntimeError(
                "Login timed out. LinkedIn may have triggered a verification "
                "challenge. Screenshot saved to /tmp/linkedin_login_failed.png. "
                "Try logging in manually once with this account to clear the challenge."
            )

        # Small human-like pause
        time.sleep(2)

        # ── Step 2: Navigate to job posting ─────────────────────────────────
        print(f"  → Loading job page: {job_url}")
        page.goto(job_url, wait_until="networkidle")

        try:
            page.wait_for_selector(".job-details-jobs-unified-top-card__job-title, h1", timeout=15_000)
        except PWTimeout:
            page.screenshot(path="/tmp/linkedin_job_failed.png")
            raise RuntimeError(
                "Could not load job page. Screenshot saved to "
                "/tmp/linkedin_job_failed.png"
            )

        # ── Step 3: Click "See more" to expand the full description ─────────
        try:
            see_more = page.locator(
                "button.jobs-description__footer-button, "
                "[aria-label*='more'], "
                "button:has-text('See more')"
            ).first
            if see_more.is_visible():
                see_more.click()
                time.sleep(1)
        except Exception:
            pass  # Not critical — continue with whatever is visible

        # ── Step 4: Extract fields ───────────────────────────────────────────
        def safe_text(selector: str) -> str:
            try:
                return page.locator(selector).first.inner_text().strip()
            except Exception:
                return ""

        job_title = (
                safe_text(".job-details-jobs-unified-top-card__job-title")
                or safe_text("h1.t-24")
                or safe_text("h1")
        )

        company = (
                safe_text(".job-details-jobs-unified-top-card__company-name")
                or safe_text("a.ember-view.t-black.t-normal")
                or safe_text(".topcard__org-name-link")
        )

        description = (
                safe_text(".jobs-description-content__text")
                or safe_text(".jobs-box__html-content")
                or safe_text("#job-details")
        )

        browser.close()

    if not job_title or not company:
        raise RuntimeError(
            f"Could not extract job title or company from {job_url}. "
            "LinkedIn may have changed its HTML structure."
        )

    return {
        "company": company,
        "job_title": job_title,
        "description": description,
    }


# ---------------------------------------------------------------------------
# S3
# ---------------------------------------------------------------------------

def _upload_description_to_s3(
        s3_client,
        job_id: str,
        description: str,
) -> str:
    """
    Upload the job description text to S3.
    Returns the S3 key.
    """
    s3_key = f"{S3_PREFIX}/{job_id}/description.txt"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=description.encode("utf-8"),
        ContentType="text/plain; charset=utf-8",
    )
    print(f"  → Uploaded description to s3://{S3_BUCKET}/{s3_key}")
    return s3_key


# ---------------------------------------------------------------------------
# DynamoDB
# ---------------------------------------------------------------------------

def _save_job_to_dynamodb(
        table,
        job_id: str,
        job_url: str,
        company: str,
        job_title: str,
        s3_key: str,
) -> None:
    """Write the job metadata record to DynamoDB."""
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

        # ── Workflow state ────────────────────────────────────────────────────
        "status": "new",

        # ── S3 reference ─────────────────────────────────────────────────────
        "s3_key_description": s3_key,

        # ── Timestamps ───────────────────────────────────────────────────────
        "created_at": ts,
        "updated_at": ts,
    }

    table.put_item(Item=item)
    print(f"  → Saved job to DynamoDB  (job_id={job_id})")


# ---------------------------------------------------------------------------
# Deduplication check
# ---------------------------------------------------------------------------

def _job_already_exists(table, job_url: str) -> bool:
    """
    Scan for an existing item with the same job_url.
    Simple protection against scraping the same posting twice.
    Note: for high volume, replace with a GSI on job_url.
    """
    resp = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr("job_url").eq(job_url),
        Limit=1,
    )
    return len(resp.get("Items", [])) > 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(job_url: str, table_name: str, region: str, profile: str | None) -> None:
    session = boto3.Session(profile_name=profile, region_name=region)
    s3 = session.client("s3")
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)

    print(f"\nJob URL  : {job_url}")
    print(f"Table    : {table_name}  ({region})")
    print(f"S3 bucket: {S3_BUCKET}\n")

    # ── Deduplicate ──────────────────────────────────────────────────────────
    if _job_already_exists(table, job_url):
        print("⚠  This job URL already exists in the table. Skipping.")
        return

    # ── Scrape ───────────────────────────────────────────────────────────────
    print("Scraping LinkedIn…")
    scraped = _scrape_with_playwright(job_url)
    print(f"  → Company  : {scraped['company']}")
    print(f"  → Job title: {scraped['job_title']}")
    print(f"  → Description length: {len(scraped['description'])} chars")

    # ── Generate internal job ID ─────────────────────────────────────────────
    # Use the LinkedIn numeric ID if available, otherwise a UUID
    linkedin_id = _extract_job_id_from_url(job_url)
    job_id = linkedin_id if linkedin_id else str(uuid.uuid4())

    # ── Upload to S3 ─────────────────────────────────────────────────────────
    s3_key = _upload_description_to_s3(s3, job_id, scraped["description"])

    # ── Save to DynamoDB ──────────────────────────────────────────────────────
    _save_job_to_dynamodb(
        table,
        job_id=job_id,
        job_url=job_url,
        company=scraped["company"],
        job_title=scraped["job_title"],
        s3_key=s3_key,
    )

    print(f"\n✓  Done.  job_id={job_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape a LinkedIn job posting and store it in S3 + DynamoDB."
    )
    parser.add_argument(
        "--url",
        required=True,
        help='LinkedIn job URL, e.g. "https://www.linkedin.com/jobs/view/1234567890"',
    )
    parser.add_argument("--table", default=DEFAULT_TABLE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--profile", default=None, help="AWS CLI profile name")
    args = parser.parse_args()

    run(args.url, args.table, args.region, args.profile)
