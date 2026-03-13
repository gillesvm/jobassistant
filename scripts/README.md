# Installation for the seed_jobs.py

Best is to use a python virtual environment for these python files to prevent bloating your system and the project.
Add the following to your gitignore file:

```
# Ignore the virtual environment
.venv/
__pycache__/
*.pyc
```

1. Install the venv module (if you don't have it):

```Bash
sudo apt update && sudo apt install python3-venv
```

2. Create and activate a virtual environment:

```Bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install your package:

```Bash
pip install boto3
```

4: *OPTIONAL* Save your dependencies:  
To let others (or your future self) know what to install, create a requirements file:

```Bash
pip freeze > requirements.txt
```

# Installation for the scrape_job.py

A few things worth noting:

**First-time setup**

```bash
pip install playwright boto3 python-dotenv
playwright install chromium
```

And your `.env` in the project root (add to `.gitignore`):

```
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=yourpassword
```

**Running it**

```bash
AWS_PROFILE=eddy python scripts/scrape_job.py --url "https://www.linkedin.com/jobs/view/1234567890"
```

**Where the migration hooks are**
The script has two clearly marked `TODO/MIGRATE` points:

- `_get_credentials()` — swap `.env` for Secrets Manager, one function body change
- `_scrape_with_playwright()` — swap Playwright for Apify, one function body change. Everything else (S3 upload,
  DynamoDB write, deduplication) stays identical

**Deduplication** — before scraping it checks if the job URL already exists in DynamoDB, so running the script twice on
the same posting is safe.

**If LinkedIn blocks you** — the script saves a screenshot to `/tmp/` when something fails, which gives you something to
debug with. The most common issue will be a verification challenge on first login with a new account, which usually
clears after logging in once manually in a real browser.