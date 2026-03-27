# About

This will become a webpage layer for my jobtracker or jobassistant where I can add jobs, edit jobs, list jobs, filter by
status and see overdue followups

# Initial file structure within jobassistant project

```
jobassistant/
  .github/
  infra/
  scripts/
  app/
    main.py
    routes/
      dashboard.py
      jobs.py
    templates/
      base.html
      dashboard.html
      jobs_list.html
      job_form.html
      job_detail.html
    static/
      styles.css
    services/
      mock_data.py
      dynamodb.py
      s3.py
    models/
      job.py
    requirements.txt
    Dockerfile
    
```

# Components

This is built using python and fastapi and bootstrap

# Usage

Run locally with these commands. Copy the .env.example file to .env and fill in the values, make sure your cli is logged
in to AWS.

```bash
# first create a virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run the app
uvicorn main:app --reload
```
