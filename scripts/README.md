# Installation

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