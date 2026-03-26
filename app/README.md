# about

this will become a webpage layer for my jobtracker or jobassistant where I can add jobs, edit jobs, list jobs, filter by
status and see overdue followups

# initial file structure within jobassistant project

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

# components

this is built using python and fastapi and bootstrap

# usage

run locally with this command

```bash
uvicorn main:app --reload
```
